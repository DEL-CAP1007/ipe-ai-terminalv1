import click
from src.core.config import get_db
from models.user import User
from services.auth.passwords import hash_password
from datetime import datetime

@click.command()
@click.option('--email', prompt=True)
@click.option('--name', prompt=True)
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True)
def create_user(email, name, password):
    db = get_db()
    user = User(
        email=email,
        display_name=name,
        password_hash=hash_password(password),
        auth_provider='local',
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(user)
    db.commit()
    click.echo(f"User {email} created.")

if __name__ == "__main__":
    create_user()
