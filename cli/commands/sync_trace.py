from services.sync import SyncService
from cli.renderers import render_sync_trace

def sync_trace_command(args):
    if not args:
        return "Usage: sync.trace <canonical_id>"
    canonical_id = args[0]
    trace = SyncService.get_trace(canonical_id)
    return render_sync_trace(trace)
