import click
from src.core.config import get_db
from models.role import Role
from models.permission import Permission
from models.role_permission import RolePermission
from models.user import User
from models.user_role import UserRole
from models.service_account import ServiceAccount
from models.service_account_role import ServiceAccountRole
from sqlalchemy.orm import Session

def populate_defaults(db: Session):
    # Default roles
    roles = [
        ("owner", "Full system access"),
        ("admin", "Manage users, secrets, triggers, pipelines"),
        ("dev", "Build & edit automation logic"),
        ("operator", "Run pipelines, sync, audits"),
        ("viewer", "Read-only"),
        ("agent", "Restricted automation identity"),
    ]
    for name, desc in roles:
        if not db.query(Role).filter_by(name=name).first():
            db.add(Role(name=name, description=desc))
    db.commit()
    # Default permissions
    perms = [
        ("system.manage", "System management"),
        ("secret.create", "Create secrets"),
        ("secret.read", "Read secrets"),
        ("secret.update", "Update secrets"),
        ("secret.delete", "Delete secrets"),
        ("sync.run", "Run sync jobs"),
        ("sync.config.edit", "Edit sync config"),
        ("entity.read.*", "Read all entities"),
        ("entity.read.task", "Read tasks"),
        ("entity.read.client", "Read clients"),
        ("entity.write.*", "Write all entities"),
        ("entity.write.task", "Write tasks"),
        ("entity.write.client", "Write clients"),
        ("entity.delete.*", "Delete all entities"),
        ("pipeline.run", "Run pipelines"),
        ("pipeline.create", "Create pipelines"),
        ("pipeline.update", "Update pipelines"),
        ("pipeline.delete", "Delete pipelines"),
        ("trigger.create", "Create triggers"),
        ("trigger.update", "Update triggers"),
        ("trigger.delete", "Delete triggers"),
        ("schema.update", "Update schema"),
        ("schema.validate", "Validate schema"),
        ("obs.view", "View observability dashboards"),
        ("audit.view", "View audit logs"),
        ("agent.run", "Run as agent"),
        ("agent.manage", "Manage agents"),
    ]
    for key, desc in perms:
        if not db.query(Permission).filter_by(key=key).first():
            db.add(Permission(key=key, description=desc))
    db.commit()
    # Default role-permission mapping (simplified)
    role_map = {
        "owner": [p[0] for p in perms],
        "admin": [
            "system.manage", "secret.create", "secret.read", "secret.update", "secret.delete",
            "pipeline.create", "pipeline.update", "pipeline.delete", "trigger.create", "trigger.update", "trigger.delete",
            "obs.view", "audit.view", "sync.run", "sync.config.edit", "entity.read.*", "entity.write.*", "entity.delete.*"
        ],
        "dev": [
            "pipeline.create", "pipeline.update", "trigger.create", "trigger.update", "schema.update", "entity.read.*", "entity.write.task", "sync.run", "obs.view", "audit.view"
        ],
        "operator": [
            "pipeline.run", "sync.run", "entity.read.*", "obs.view", "audit.view"
        ],
        "viewer": [
            "entity.read.*", "obs.view"
        ],
        "agent": [
            "agent.run"
        ],
    }
    for role_name, perm_keys in role_map.items():
        role = db.query(Role).filter_by(name=role_name).first()
        for key in perm_keys:
            perm = db.query(Permission).filter_by(key=key).first()
            if role and perm and not db.query(RolePermission).filter_by(role_id=role.id, permission_id=perm.id).first():
                db.add(RolePermission(role_id=role.id, permission_id=perm.id))
    db.commit()

@click.command()
def rbac_populate():
    db = get_db()
    populate_defaults(db)
    click.echo("Default roles and permissions populated.")

if __name__ == "__main__":
    rbac_populate()
