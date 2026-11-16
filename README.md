# styne-sdk

Python client for the [Styne](https://styne.ai) API: VMs and cloud browsers.

```bash
pip install styne-sdk
export STYNE_API_KEY=...
```

Python 3.11 to 3.13. The sync client (`styne.Client`, `styne.Vm`, `styne.Browser`) and the async client
(`styne.AsyncClient`, `styne.AsyncVm`, `styne.AsyncBrowser`) have the same methods. Records the API returns
(`vm.info`, snapshots, ports, checkpoints) are typed classes from `styne.models`.

## Regions

```python
client = styne.Client(region="ams")  # "ash" (US East, default) or "ams" (Europe); or set STYNE_REGION
```

Without `region` the client uses `https://ash.api.styne.ai`, and a create that names no region starts in the region of that host. Accepted names:
`ash` (also `us-east`, `ashburn`) and `ams` (also `eu`, `eu-central`), in any case. `base_url` and `STYNE_BASE_URL` take precedence over `region`
and `STYNE_REGION`, so an environment value of `STYNE_BASE_URL` decides where the key is sent; an unknown region name always raises. A create from a snapshot
stays in the snapshot's region. See [Regions](https://docs.styne.ai/regions).

## Run a command in a VM

```python
import styne

client = styne.Client()  # reads STYNE_API_KEY

with client.vms.create(size="small") as vm:  # the VM is deleted when the block ends
    result = vm.run("echo hello && uname -r")
    print(result.stdout, result.exit_code)
    result.check()  # raises CommandError on a non-zero exit

    vm.files.write("/work/app.py", "print('hi')")
    print(vm.run("python3 /work/app.py").stdout)
    for event in vm.stream("for i in 1 2 3; do echo $i; sleep 1; done"):
        print(event.type, event.data)
```

`vm.run` waits as long as the command runs unless you pass `timeout=` (seconds). A command is sent once and never
retried.

## Checkpoint, pause, fork and snapshot

```python
vm = client.vms.create()
before = vm.checkpoints.create("before-migration")
vm.run("./migrate.sh")
vm.rewind(before)  # back to the checkpoint

vm.pause()  # state is kept, billing stops
vm.resume()
copies = vm.fork(count=3)  # three running copies of this VM
snap = vm.snapshot("ready")
other = client.snapshots.start(snap.id)
url = vm.ports.expose(8080, public=True).url

for copy in [*copies, other, vm]:
    copy.kill()
client.snapshots.delete(snap.id)
```

## A cloud browser for Playwright

```python
from playwright.sync_api import sync_playwright

with client.browsers.create() as browser, sync_playwright() as p:
    page = p.chromium.connect_over_cdp(browser.cdp_url).contexts[0].new_page()
    page.goto("https://example.com")
    print(page.title(), browser.live_view_url)
    control = browser.take_control("alice@example.com")  # names the person in the audit log; agent input pauses
    print(control.cdp_url)
    browser.give_back_control()
```

### Keep a session through a dropped socket

The browser, its pages and their state live on the server, so a closed CDP socket does not end the session.
`browser.with_reconnect` reads the session again, connects again and calls your function again (up to 5 times by default):

```python
def work(pw_browser, attempt):
    context = pw_browser.contexts[0]
    page = context.pages[0] if context.pages else context.new_page()
    if attempt == 0:
        page.goto("https://example.com")
    return page.title()


title = browser.with_reconnect(p.chromium.connect_over_cdp, work)
```

Start from `context.pages`, not from a page object you kept. Options: `max_reconnects`, `delay` (seconds), `is_disconnect` (which errors mean a closed socket; `styne.is_disconnect` is the default). `run` starts
again from the top, so it must be safe to repeat, and it owns the Playwright browser it is given. `AsyncBrowser.with_reconnect` is the asyncio form. Errors that are not a closed socket are raised unchanged.

`examples/` has runnable versions of the VM, fork and browser snippets.

## Async

```python
import asyncio
import styne


async def main() -> None:
    async with styne.AsyncClient() as client:
        async with await client.vms.create() as vm:
            print((await vm.run("date")).stdout)


asyncio.run(main())
```

## Errors, retries and idempotency

Every error is a `styne.StyneError`:

- `styne.APIError` (the API answered with an error) has `status`, `code`, `origin`, `request_id`, `details`,
  `doc_url` and `retry_after`. Subclasses: `InvalidArgumentError`, `IdempotencyMismatchError`,
  `AuthenticationError`, `PaymentRequiredError`, `PlanRequiredError`, `PermissionDeniedError`, `NotFoundError`,
  `VmEndedError`, `ConflictError`, `QuotaExceededError`, `RateLimitError`, `LimitConcurrentError`,
  `CapacityError`, `CommandTimeoutError`, `ServerError`.
- `styne.APIConnectionError` (no answer arrived) and its subclass `styne.APITimeoutError`.
- `styne.CommandError` from `CommandResult.check()`.

```python
try:
    client.vms.create()
except styne.LimitConcurrentError as err:
    print(err.details, err.request_id)
```

Reads and deletes, and the creates the API deduplicates by `Idempotency-Key` (VMs, browsers, forks, snapshots,
checkpoints), are retried on network errors, 408, 429, 5xx and in-flight 409 answers, honouring `Retry-After`.
Every other call, a command above all, is sent once. `Client(max_retries=2, timeout=60)` tunes both.
`http_client=` takes your own `httpx.Client` (proxies, limits); the key and URL are still applied.

## Development

```bash
pip install -e '.[dev]'
tools/generate.sh   # refresh src/styne/_generated from openapi.yaml
ruff check . && mypy src tests && pytest
STYNE_API_KEY=... pytest -m live
```

Apache-2.0.
