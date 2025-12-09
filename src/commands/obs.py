import click
from services.telemetry_repository import TelemetryRepository
from src.core.config import get_db
from datetime import datetime, timedelta

@click.group()
def obs():
    """Observability dashboards"""
    pass

@obs.command()
def status():
    """Show overall system health"""
    db = get_db()
    # Example metrics
    last_sync = TelemetryRepository.get_latest(db, 'sync_jobs')
    last_trigger = TelemetryRepository.get_latest(db, 'trigger_runs')
    last_schema = TelemetryRepository.get_latest(db, 'schema_violations')
    last_rel = TelemetryRepository.get_latest(db, 'entity_relations')
    last_event = TelemetryRepository.get_latest(db, 'events')
    click.echo("=== IPE Automation System — Health Overview ===")
    click.echo(f"Sync Engine:\n  Last Sync:         {last_sync.timestamp if last_sync else '-'}\n  Jobs:              {last_sync.value if last_sync else '-'}")
    click.echo(f"Triggers:\n  Last Fired:        {last_trigger.timestamp if last_trigger else '-'}\n  Runs:              {last_trigger.value if last_trigger else '-'}")
    click.echo(f"Schema Validator:\n  Violations:        {last_schema.value if last_schema else '-'}")
    click.echo(f"Relationships:\n  Total:             {last_rel.value if last_rel else '-'}")
    click.echo(f"System Load:\n  Events:            {last_event.value if last_event else '-'}")

@obs.command()
def sync():
    """Show sync dashboard"""
    db = get_db()
    metrics = TelemetryRepository.get_metrics(db, 'sync_jobs', datetime.utcnow() - timedelta(days=1), datetime.utcnow())
    click.echo("=== Sync Dashboard ===")
    for m in metrics:
        click.echo(f"{m.timestamp:%H:%M}   {m.value}")

@obs.command()
def triggers():
    """Show trigger dashboard"""
    db = get_db()
    metrics = TelemetryRepository.get_metrics(db, 'trigger_runs', datetime.utcnow() - timedelta(days=1), datetime.utcnow())
    click.echo("=== Trigger Engine Status ===")
    for m in metrics:
        click.echo(f"{m.timestamp:%H:%M}   {m.value}")

@obs.command()
def schema():
    """Show schema integrity dashboard"""
    db = get_db()
    metrics = TelemetryRepository.get_metrics(db, 'schema_violations', datetime.utcnow() - timedelta(days=1), datetime.utcnow())
    click.echo("=== Schema Integrity ===")
    for m in metrics:
        click.echo(f"{m.timestamp:%H:%M}   {m.value}")

@obs.command()
def relations():
    """Show relationship graph health"""
    db = get_db()
    metrics = TelemetryRepository.get_metrics(db, 'entity_relations', datetime.utcnow() - timedelta(days=1), datetime.utcnow())
    click.echo("=== Relationship Graph Health ===")
    for m in metrics:
        click.echo(f"{m.timestamp:%H:%M}   {m.value}")

@obs.command()
def events():
    """Show event log viewer"""
    db = get_db()
    metrics = TelemetryRepository.get_metrics(db, 'events', datetime.utcnow() - timedelta(days=1), datetime.utcnow())
    click.echo("=== Event Log ===")
    for m in metrics:
        click.echo(f"{m.timestamp:%H:%M}   {m.value}")

@obs.command()
def drift():
    """Run drift detection"""
    db = get_db()
    metrics = TelemetryRepository.get_metrics(db, 'drift', datetime.utcnow() - timedelta(days=1), datetime.utcnow())
    click.echo("=== Drift Detection ===")
    for m in metrics:
        click.echo(f"{m.timestamp:%H:%M}   {m.value}")
