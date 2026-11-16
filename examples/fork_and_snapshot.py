import styne

client = styne.Client()
vm = client.vms.create()
try:
    snap = vm.snapshot("ready")
    copies = vm.fork(count=2)
    print([copy.id for copy in copies], snap.id)
    for copy in copies:
        copy.kill()
    client.snapshots.delete(snap.id)
finally:
    vm.kill()
