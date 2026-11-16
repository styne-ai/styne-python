"""Exceptions raised by the SDK.

``StyneError`` is the base of all of them. ``APIError`` and its subclasses carry an HTTP answer;
``APIConnectionError`` (and its ``APITimeoutError`` subclass) means no answer arrived; ``CommandError``
is raised by :meth:`styne.CommandResult.check` for a non-zero exit.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Mapping, Optional, Type

if TYPE_CHECKING:
    from .types import CommandResult


class StyneError(Exception):
    """Base class for every error this SDK raises."""


class APIConnectionError(StyneError):
    """The request never produced an HTTP response (DNS, TLS, connection reset)."""


class APITimeoutError(APIConnectionError):
    """The request exceeded the client timeout."""


class CommandError(StyneError):
    """A command exited with a non-zero code; raised by :meth:`styne.CommandResult.check`."""

    def __init__(self, result: CommandResult) -> None:
        super().__init__(f"command exited with {result.exit_code}: {result.stderr.strip()[:200]}")
        self.result = result


class APIError(StyneError):
    """The API answered with an error status."""

    def __init__(
        self,
        message: str,
        *,
        status: int,
        code: str = "unknown",
        origin: Optional[str] = None,
        request_id: Optional[str] = None,
        details: Optional[Mapping[str, Any]] = None,
        doc_url: Optional[str] = None,
        retry_after: Optional[float] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status = status
        self.code = code
        self.origin = origin
        self.request_id = request_id
        self.details: Dict[str, Any] = dict(details or {})
        self.doc_url = doc_url
        self.retry_after = retry_after

    def __str__(self) -> str:
        suffix = f" (request {self.request_id})" if self.request_id else ""
        return f"{self.status} {self.code}: {self.message}{suffix}"


class InvalidArgumentError(APIError):
    """The request is malformed or a field is invalid (400, 422)."""


class IdempotencyMismatchError(InvalidArgumentError):
    """An Idempotency-Key was reused with a different body (422)."""


class AuthenticationError(APIError):
    """The API key is invalid or revoked (401)."""


class PaymentRequiredError(APIError):
    """The account needs credit or a payment method (402)."""


class PlanRequiredError(PaymentRequiredError):
    """The action needs a higher plan (402)."""


class PermissionDeniedError(APIError):
    """The key lacks the scope for this action, or the account is suspended (403)."""


class NotFoundError(APIError):
    """The object does not exist (404)."""


class VmEndedError(APIError):
    """The VM has ended and can no longer run commands."""


class ConflictError(APIError):
    """The request conflicts with the current state (409)."""


class QuotaExceededError(APIError):
    """A usage quota of the plan (hours, storage) is used up."""


class RateLimitError(APIError):
    """A rate limit was hit (429); see ``retry_after``."""


class LimitConcurrentError(RateLimitError):
    """The plan's limit on resources running at the same time is reached."""


class CapacityError(APIError):
    """No capacity is free in the region right now; retry later or pick another region."""


class CommandTimeoutError(APIError):
    """A command ran past its timeout."""


class ServerError(APIError):
    """The service failed (5xx)."""


_BY_CODE: Dict[str, Type[APIError]] = {
    "unauthenticated": AuthenticationError,
    "permission_denied": PermissionDeniedError,
    "account_suspended": PermissionDeniedError,
    "plan_required": PlanRequiredError,
    "payment_required": PaymentRequiredError,
    "not_found": NotFoundError,
    "vm_ended": VmEndedError,
    "conflict": ConflictError,
    "failed_precondition": ConflictError,
    "invalid_argument": InvalidArgumentError,
    "idempotency_mismatch": IdempotencyMismatchError,
    "quota_exceeded": QuotaExceededError,
    "limit_hours": QuotaExceededError,
    "limit_storage": QuotaExceededError,
    "limit_concurrent": LimitConcurrentError,
    "limit_rate_minute": RateLimitError,
    "limit_rate_hour": RateLimitError,
    "limit_rate_day": RateLimitError,
    "account_throttled": RateLimitError,
    "capacity": CapacityError,
    "capacity_provisioning": CapacityError,
    "command_timeout": CommandTimeoutError,
}

_BY_STATUS: Dict[int, Type[APIError]] = {
    400: InvalidArgumentError,
    401: AuthenticationError,
    402: PaymentRequiredError,
    403: PermissionDeniedError,
    404: NotFoundError,
    409: ConflictError,
    422: InvalidArgumentError,
    429: RateLimitError,
}


def error_from_payload(
    status: int,
    payload: Any,
    *,
    request_id: Optional[str] = None,
    retry_after: Optional[float] = None,
) -> APIError:
    """Build the matching exception from a decoded error body."""
    body: Mapping[str, Any] = payload if isinstance(payload, dict) else {}
    inner = body.get("error")
    fields: Mapping[str, Any] = inner if isinstance(inner, dict) else {}
    code = fields.get("code")
    code = code if isinstance(code, str) else "unknown"
    message = (
        fields.get("message") or body.get("message") or (inner if isinstance(inner, str) else None) or f"HTTP {status}"
    )
    cls = _BY_CODE.get(code) or _BY_STATUS.get(status) or (ServerError if status >= 500 else APIError)
    details = fields.get("details")
    return cls(
        str(message),
        status=status,
        code=code,
        origin=fields.get("origin"),
        request_id=fields.get("request_id") or request_id,
        details=details if isinstance(details, dict) else None,
        doc_url=body.get("doc_url") or fields.get("doc_url"),
        retry_after=retry_after,
    )
