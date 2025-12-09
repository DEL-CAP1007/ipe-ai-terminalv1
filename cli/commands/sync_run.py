from services.sync import SyncService

def sync_run_command(args):
    entity_type = args[0] if args else None
    job_id = SyncService.run(entity_type=entity_type)
    return f"Sync job started: {job_id}"
