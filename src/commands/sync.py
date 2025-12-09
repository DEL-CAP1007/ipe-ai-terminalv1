import click
from core.sync_manager import SyncManager

@click.group()
def cli():
    pass

@cli.command()
@click.option('--fast', is_flag=True, help='Only sync recent changes')
@click.argument('table', required=False)
def sync(fast, table):
    """Run a full or partial sync cycle."""
    manager = SyncManager()
    mode = 'fast' if fast else 'full'
    result = manager.sync(mode=mode, table=table)
    click.echo(f"Sync complete. Diff report: {result}")

@cli.command()
@click.argument('table', required=False)
def diff(table):
    """Show inconsistencies between Notion and T7."""
    manager = SyncManager()
    result = manager.diff(table=table)
    click.echo(f"Diff report: {result}")

if __name__ == '__main__':
    cli()
