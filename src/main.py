import os
import click
from core.dispatcher import dispatch_command
from commands.ipe_os import build_ipe_os
from src.commands import roles
from src.commands import auth
from src.commands import obs
from src.commands import secret
from src.commands import token
from src.commands import audit

@click.command()
@click.argument("command", nargs=-1)
def cli(command):
    # Workflow engine
    if command and command[0] == "workflow":
        from commands.workflow import run_workflow
        # Workflows that require a date argument
        workflows_with_date = [
            "timeline-event", "timeline-k12", "timeline-accelerator",
            "daily-cycle", "weekly-cycle", "monthly-cycle", "countdown-event", "followup-event", "full-event-schedule"
        ]
        if len(command) >= 4 and command[1] in workflows_with_date:
            workflow_name = command[1]
            target_name = command[2]
            date_arg = command[3]
            run_workflow(workflow_name, target_name, date_arg)
            return
        elif len(command) >= 3:
            workflow_name = command[1]
            target_name = " ".join(command[2:])
            run_workflow(workflow_name, target_name)
            return
        else:
            print("Usage: workflow <workflow_name> <target_name> [date]")
            return
    # Custom sync commands
    if command and command[0] == "sync-all":
        from commands.filesystem import LOCAL_ROOT, CLOUD_ROOT, sync_folder
        sync_folder(LOCAL_ROOT, CLOUD_ROOT)
        print("\n=== FULL SYNC COMPLETE ===\n")
        return
    if command and command[0] == "sync-event":
        event_name = command[1] if len(command) > 1 else None
        if not event_name:
            print("Usage: sync-event <event_name>")
            return
        local = f"/Volumes/T7/IPE/Events/{event_name}"
        cloud = os.path.expanduser(f"~/OneDrive - IPE Enterprise/IPE/Events/{event_name}")
        from commands.filesystem import sync_folder
        sync_folder(local, cloud)
        print(f"\n=== SYNCED EVENT: {event_name} ===\n")
        return
    if command and command[0] == "sync-client":
        client_name = command[1] if len(command) > 1 else None
        if not client_name:
            print("Usage: sync-client <client_name>")
            return
        local = f"/Volumes/T7/IPE/Clients/{client_name}"
        cloud = os.path.expanduser(f"~/OneDrive - IPE Enterprise/IPE/Clients/{client_name}")
        from commands.filesystem import sync_folder
        sync_folder(local, cloud)
        print(f"\n=== SYNCED CLIENT: {client_name} ===\n")
        return
    # IPE OS builder command
    if command and command[0] == "notion" and len(command) > 1:
        action = command[1]
        if action == "build-ipe-os":
            build_ipe_os()
            return
        elif action == "list-databases":
            from commands.notion_inspect import list_all_databases
            list_all_databases()
            return
    # Entry point for the AI Terminal
    dispatch_command(command)

if __name__ == "__main__":
    cli()
    # Register roles CLI
    roles.roles()
    # Register auth CLI
    auth.auth()
    # Register obs CLI
    obs.obs()
    # Register secret CLI
    secret.register_secret_commands(roles)
    # Register token CLI
    token.register_token_commands(roles)
    # Register audit CLI
    audit.register_audit_commands(roles)
