import click
from core.sync_manager import SyncManager

@click.group()
def cli():
    pass

@cli.command()
@click.option('--all', is_flag=True, help='Test all tables')
@click.argument('table', required=False)
def test(all, table):
    """Run sync tests for all or a specific table."""
    manager = SyncManager()
    tables = manager.notion.db_ids.keys() if all else [table]
    report = {}
    for t in tables:
        notion_data = manager.notion.pull(table=t)
        t7_data = manager.t7.pull(table=t)
        # Orphaned records
        notion_ids = {r.id for r in notion_data.get(t, [])}
        t7_ids = {r.id for r in t7_data.get(t, [])}
        report[t] = {
            'orphaned_in_notion': list(notion_ids - t7_ids),
            'orphaned_in_t7': list(t7_ids - notion_ids),
            'broken_relationships': [],  # Placeholder
            'desync_statuses': [],       # Placeholder
            'hash_mismatches': [rid for rid in notion_ids & t7_ids if next((r for r in notion_data[t] if r.id == rid), None).hash != next((r for r in t7_data[t] if r.id == rid), None).hash],
            'unmapped_fields': []        # Placeholder
        }
    click.echo(report)

if __name__ == '__main__':
    cli()
