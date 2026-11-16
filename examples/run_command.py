import styne

client = styne.Client()
with client.vms.create(size="small") as vm:
    result = vm.run("echo hello && uname -r")
    print(result.stdout, result.exit_code)
