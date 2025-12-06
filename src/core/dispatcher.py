
from commands.help import run_help
from commands.generate import run_generate
from commands.notion import run_notion
## from commands.schedule import run_schedule  # Removed: not needed for workflow CLI
from commands.filesystem import install_master_folders

def dispatch_command(args):
    if not args:
        run_help()
        return
    
    cmd = args[0]

    if cmd == "help":
        run_help()

    elif cmd == "generate":
        run_generate(args[1:])


    elif cmd == "notion":
        run_notion(args[1:])

    elif cmd == "schedule":
        run_schedule(args[1:])

    elif cmd == "filesystem" and len(args) > 1 and args[1] == "install-folders":
        install_master_folders()
    else:
        print(f"[ERROR] Unknown command: {cmd}")
        run_help()
