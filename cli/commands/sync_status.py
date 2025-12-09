from services.sync import SyncService
from cli.renderers import render_sync_status

def sync_status_command(args):
    status = SyncService.get_status()
    return render_sync_status(status)
