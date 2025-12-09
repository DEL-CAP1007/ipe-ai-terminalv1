import json
from services.auth.token_service import TokenService
from db.session import get_session
from services.auth.identity import get_identity

def token_create_command(args):
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--scopes', nargs='+', required=True)
    parser.add_argument('--description', type=str, default=None)
    parser.add_argument('--ttl', type=str, default=None)
    opts = parser.parse_args(args)
    scopes = opts.scopes
    description = opts.description
    ttl_hours = None
    if opts.ttl:
        if opts.ttl.endswith('h'):
            ttl_hours = int(opts.ttl[:-1])
        elif opts.ttl.endswith('d'):
            ttl_hours = int(opts.ttl[:-1]) * 24
        else:
            ttl_hours = int(opts.ttl)
    with get_session() as db:
        identity = get_identity()
        raw = TokenService.create_token(db, identity, scopes, description, ttl_hours)
        print("=== API Token (store securely, shown only once) ===\n" + raw)

def token_list_command(args):
    from models.api_token import ApiToken
    with get_session() as db:
        identity = get_identity()
        tokens = db.query(ApiToken).filter(
            (ApiToken.owner_user_id == identity.subject_id) | (ApiToken.owner_service_id == identity.subject_id)
        ).all()
        print("=== API Tokens ===")
        print(f"{'ID':<36}{'Description':<25}{'Scopes':<30}{'Expires':<20}{'Last Used'}")
        for t in tokens:
            scopes = t.scopes if isinstance(t.scopes, list) else t.scopes.get('scopes', [])
            print(f"{str(t.id):<36}{(t.description or '')[:24]:<25}{len(scopes)} scopes{'':<18}{str(t.expires_at)[:19]:<20}{str(t.last_used_at)[:19] if t.last_used_at else '-'}")

def token_revoke_command(args):
    if not args:
        print("Usage: token.revoke <TOKEN_ID>")
        return
    token_id = args[0]
    from models.api_token import ApiToken
    with get_session() as db:
        identity = get_identity()
        token = db.query(ApiToken).filter_by(id=token_id).one_or_none()
        if not token:
            print("Token not found.")
            return
        # Only owner can revoke
        if (token.owner_user_id != identity.subject_id) and (token.owner_service_id != identity.subject_id):
            print("Not authorized to revoke this token.")
            return
        db.delete(token)
        db.commit()
        print(f"Token {token_id} revoked.")

def token_scope_add_command(args):
    if len(args) < 2:
        print("Usage: token.scope.add <TOKEN_ID> <SCOPE>")
        return
    token_id, scope = args[0], args[1]
    from models.api_token import ApiToken
    with get_session() as db:
        identity = get_identity()
        token = db.query(ApiToken).filter_by(id=token_id).one_or_none()
        if not token:
            print("Token not found.")
            return
        scopes = token.scopes if isinstance(token.scopes, list) else token.scopes.get('scopes', [])
        if scope in scopes:
            print("Scope already present.")
            return
        scopes.append(scope)
        token.scopes = scopes
        db.commit()
        print(f"Scope '{scope}' added to token {token_id}.")

def token_scope_remove_command(args):
    if len(args) < 2:
        print("Usage: token.scope.remove <TOKEN_ID> <SCOPE>")
        return
    token_id, scope = args[0], args[1]
    from models.api_token import ApiToken
    with get_session() as db:
        identity = get_identity()
        token = db.query(ApiToken).filter_by(id=token_id).one_or_none()
        if not token:
            print("Token not found.")
            return
        scopes = token.scopes if isinstance(token.scopes, list) else token.scopes.get('scopes', [])
        if scope not in scopes:
            print("Scope not present.")
            return
        scopes.remove(scope)
        token.scopes = scopes
        db.commit()
        print(f"Scope '{scope}' removed from token {token_id}.")

def register_token_commands(registry):
    registry.register("token.create", token_create_command)
    registry.register("token.list", token_list_command)
    registry.register("token.revoke", token_revoke_command)
    registry.register("token.scope.add", token_scope_add_command)
    registry.register("token.scope.remove", token_scope_remove_command)

# Agent profiles (scope bundles)
AGENT_PROFILES = {
    "ops_agent": ["entity.read.*", "entity.write.task.status", "pipeline.run", "obs.view"],
    "sync_agent": ["sync.run", "entity.read.*", "obs.view"],
    "relationship_agent": ["entity.read.*", "entity.write.*", "relations.read", "relations.write"]
}
