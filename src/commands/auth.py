import click
import getpass
import os
import json
from src.core.config import get_db
from services.auth.service import AuthService
from services.auth.identity import get_current_identity

CONFIG_PATH = os.path.expanduser("~/.ipe-terminal/config.json")

@click.group()
def auth():
    """Authentication commands"""
    pass

@auth.command()
def login():
    """Log in to the system"""
    email = input("Email: ")
    password = getpass.getpass("Password: ")
    db = get_db()
    try:
        session = AuthService.login(db, email, password)
        session_id = str(session.id)
        # Store session_id in config
        config = {"session_id": session_id}
        with open(CONFIG_PATH, "w") as f:
            json.dump(config, f)
        click.echo(f"Logged in as {email}")
    except Exception as e:
        click.echo(f"Login failed: {e}")

@auth.command()
def whoami():
    """Show current identity"""
    # Load session_id from config
    try:
        with open(CONFIG_PATH) as f:
            config = json.load(f)
        session_id = config.get("session_id")
    except Exception:
        session_id = None
    if not session_id:
        click.echo("Not logged in.")
        return
    db = get_db()
    identity = get_current_identity(db, session_id)
    if not identity:
        click.echo("Session expired or invalid.")
        return
    click.echo(f"Identity: {identity.subject_type}")
    click.echo(f"Name:    {identity.display_name}")
    if identity.email:
        click.echo(f"Email:   {identity.email}")
    if identity.name:
        click.echo(f"Service: {identity.name}")

@auth.command()
def logout():
    """Log out of the system"""
    try:
        with open(CONFIG_PATH) as f:
            config = json.load(f)
        session_id = config.get("session_id")
    except Exception:
        session_id = None
    if not session_id:
        click.echo("Not logged in.")
        return
    db = get_db()
    AuthService.logout(db, session_id)
    os.remove(CONFIG_PATH)
    click.echo("Logged out.")
