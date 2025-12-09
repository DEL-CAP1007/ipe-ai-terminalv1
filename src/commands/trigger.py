import click
from models.trigger import Trigger
from services.trigger_repository import TriggerRepository
from services.trigger_engine import EventBus
from src.core.config import get_db

@click.group()
def trigger():
    """Manage triggers"""
    pass

@trigger.command()
def list():
    """List all triggers"""
    db = get_db()
    triggers = TriggerRepository.list_all(db)
    for t in triggers:
        click.echo(f"{t.id}: {t.name} [{t.event_type}] Enabled: {t.is_enabled}")

@trigger.command()
@click.argument('name')
@click.argument('event_type')
@click.option('--condition', default=None, help='Python condition expression')
@click.option('--action', default=None, help='Python action code')
def add(name, event_type, condition, action):
    """Add a new trigger"""
    db = get_db()
    trigger = Trigger(name=name, event_type=event_type, condition=condition, action=action, is_enabled=True)
    TriggerRepository.add(db, trigger)
    click.echo(f"Added trigger {trigger.id}: {trigger.name}")

@trigger.command()
@click.argument('trigger_id', type=int)
def remove(trigger_id):
    """Remove a trigger"""
    db = get_db()
    TriggerRepository.remove(db, trigger_id)
    click.echo(f"Removed trigger {trigger_id}")

@trigger.command()
@click.argument('trigger_id', type=int)
def enable(trigger_id):
    """Enable a trigger"""
    db = get_db()
    TriggerRepository.enable(db, trigger_id)
    click.echo(f"Enabled trigger {trigger_id}")

@trigger.command()
@click.argument('trigger_id', type=int)
def disable(trigger_id):
    """Disable a trigger"""
    db = get_db()
    TriggerRepository.disable(db, trigger_id)
    click.echo(f"Disabled trigger {trigger_id}")

@trigger.command()
@click.argument('trigger_id', type=int)
def runs(trigger_id):
    """Show trigger runs"""
    db = get_db()
    runs = TriggerRepository.get_runs(db, trigger_id)
    for r in runs:
        click.echo(f"Run {r.id}: {r.status} {r.started_at} -> {r.finished_at}")

@trigger.command()
@click.argument('event_type')
@click.option('--payload', default="{}", help='Event payload as JSON')
def test(event_type, payload):
    """Test trigger evaluation for an event"""
    import json
    db = get_db()
    bus = EventBus(db)
    bus.emit(event_type, json.loads(payload))
    click.echo(f"Test event '{event_type}' emitted.")
