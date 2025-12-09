import click
from src.core.config import get_db
from models.role import Role
from models.permission import Permission
from models.role_permission import RolePermission
from sqlalchemy.orm import Session

@click.group()
def roles():
    """Role and permission management"""
    pass

@roles.command()
def list():
    """List all roles"""
    db = get_db()
    roles = db.query(Role).all()
    click.echo("Role         Description")
    for r in roles:
        click.echo(f"{r.name:<12} {r.description}")

@roles.command()
@click.argument('role')
def permissions(role):
    """Show permissions for a role"""
    db = get_db()
    r = db.query(Role).filter_by(name=role).first()
    if not r:
        click.echo(f"Role '{role}' not found.")
        return
    perms = (
        db.query(Permission.key)
        .join(RolePermission, RolePermission.permission_id == Permission.id)
        .filter(RolePermission.role_id == r.id)
        .all()
    )
    click.echo(f"Permissions for role '{role}':")
    for p in perms:
        click.echo(f" - {p[0]}")

@roles.command()
@click.argument('user_email')
@click.argument('role')
def assign(user_email, role):
    """Assign a role to a user"""
    from models.user import User
    from models.user_role import UserRole
    db = get_db()
    user = db.query(User).filter_by(email=user_email).first()
    r = db.query(Role).filter_by(name=role).first()
    if not user or not r:
        click.echo("User or role not found.")
        return
    if not db.query(UserRole).filter_by(user_id=user.id, role_id=r.id).first():
        db.add(UserRole(user_id=user.id, role_id=r.id))
        db.commit()
        click.echo(f"Assigned role '{role}' to {user_email}.")
    else:
        click.echo(f"User already has role '{role}'.")

@roles.command()
@click.argument('user_email')
@click.argument('role')
def revoke(user_email, role):
    """Revoke a role from a user"""
    from models.user import User
    from models.user_role import UserRole
    db = get_db()
    user = db.query(User).filter_by(email=user_email).first()
    r = db.query(Role).filter_by(name=role).first()
    if not user or not r:
        click.echo("User or role not found.")
        return
    ur = db.query(UserRole).filter_by(user_id=user.id, role_id=r.id).first()
    if ur:
        db.delete(ur)
        db.commit()
        click.echo(f"Revoked role '{role}' from {user_email}.")
    else:
        click.echo(f"User does not have role '{role}'.")
