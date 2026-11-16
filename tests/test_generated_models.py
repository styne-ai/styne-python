from __future__ import annotations

import importlib
import pkgutil

from styne._generated import models
from styne.models import UNSET, BrowserInfo, Snapshot, VmInfo


def test_every_generated_model_imports() -> None:
    names = [m.name for m in pkgutil.iter_modules(models.__path__)]
    assert len(names) > 50
    for name in names:
        importlib.import_module(f"styne._generated.models.{name}")


def test_vm_round_trip() -> None:
    raw = {"id": "vm_1", "state": "paused", "pause_tier": "hot", "created_at": "2026-11-16T10:00:00Z", "vcpus": 2}
    vm = VmInfo.from_dict(raw)
    assert (vm.id, vm.vcpus) == ("vm_1", 2)
    assert vm.to_dict()["state"] == "paused"


def test_browser_and_snapshot_parse() -> None:
    browser = BrowserInfo.from_dict({"id": "br_1", "state": "running", "cdp_url": "wss://x"})
    assert browser.cdp_url == "wss://x"
    assert Snapshot.from_dict({"id": "s1", "size_bytes": 5}).size_bytes == 5
    assert Snapshot.from_dict({"id": "s1"}).name is UNSET
