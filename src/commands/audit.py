from db.session import get_session
from models.audit_log import AuditLog

def audit_tail_command(args):
    N = 20
    for i, arg in enumerate(args):
        if arg.isdigit():
            N = int(arg)
    with get_session() as db:
        logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(N).all()
        print(f"=== Audit Log (last {N}) ===")
        for log in reversed(logs):
            print(f"{str(log.created_at)[:19]}  {log.actor_label or log.actor_type}:{log.actor_id[:8]}  {log.action:<15}  {log.target_label or log.target_id or '-':<20}  {log.status}")

def audit_entity_command(args):
    if not args:
        print("Usage: audit.entity <canonical_id>")
        return
    entity_id = args[0]
    with get_session() as db:
        logs = db.query(AuditLog).filter(AuditLog.target_id == entity_id).order_by(AuditLog.created_at.desc()).all()
        print(f"=== Audit for entity {entity_id} ===")
        for log in reversed(logs):
            print(f"{str(log.created_at)[:19]}  {log.actor_label or log.actor_type}:{log.actor_id[:8]}  {log.action:<15}  {log.metadata.get('diff', '-')}")

def audit_actor_command(args):
    if not args:
        print("Usage: audit.actor <actor_id>")
        return
    actor_id = args[0]
    with get_session() as db:
        logs = db.query(AuditLog).filter(AuditLog.actor_id == actor_id).order_by(AuditLog.created_at.desc()).all()
        print(f"=== Audit for actor {actor_id} ===")
        for log in reversed(logs):
            print(f"{str(log.created_at)[:19]}  {log.action:<15}  {log.target_label or log.target_id or '-':<20}  {log.status}")

def audit_action_command(args):
    if not args:
        print("Usage: audit.action <action_name>")
        return
    action = args[0]
    with get_session() as db:
        logs = db.query(AuditLog).filter(AuditLog.action == action).order_by(AuditLog.created_at.desc()).all()
        print(f"=== Audit for action {action} ===")
        for log in reversed(logs):
            print(f"{str(log.created_at)[:19]}  {log.actor_label or log.actor_type}:{log.actor_id[:8]}  {log.target_label or log.target_id or '-':<20}  {log.status}")

def register_audit_commands(registry):
    registry.register("audit.tail", audit_tail_command)
    registry.register("audit.entity", audit_entity_command)
    registry.register("audit.actor", audit_actor_command)
    registry.register("audit.action", audit_action_command)
