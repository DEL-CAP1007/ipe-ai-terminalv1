from getpass import getpass
from services.secret.service import SecretService
from db.session import get_session
from services.auth.identity import get_identity


def secret_list_command(args):
    with get_session() as db:
        identity = get_identity()
        secrets = SecretService.list_secrets(db, identity)
        print("=== Secrets ===")
        print(f"{'Name':<20}{'Scope':<10}{'Description':<30}{'Updated'}")
        for s in secrets:
            print(f"{s['name']:<20}{s['scope']:<10}{s['description'] or '':<30}{s['updated_at']}")

def secret_set_command(args):
    if not args:
        print("Usage: secret.set <NAME> [--scope scope]")
        return
    name = args[0]
    scope = "system"
    if "--scope" in args:
        idx = args.index("--scope")
        scope = args[idx+1]
    value = getpass(f"Enter value for {name}: ")
    with get_session() as db:
        identity = get_identity()
        SecretService.set_secret(db, identity, name, value, scope=scope)
        print(f"Secret '{name}' set (scope={scope}).")

def secret_delete_command(args):
    if not args:
        print("Usage: secret.delete <NAME>")
        return
    name = args[0]
    with get_session() as db:
        identity = get_identity()
        ok = SecretService.delete_secret(db, identity, name)
        if ok:
            print(f"Secret '{name}' deleted.")
        else:
            print(f"Secret '{name}' not found.")

def register_secret_commands(registry):
    registry.register("secret.list", secret_list_command)
    registry.register("secret.set", secret_set_command)
    registry.register("secret.delete", secret_delete_command)
