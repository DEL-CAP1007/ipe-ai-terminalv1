from connectors.notion_connector import NotionConnector
from connectors.t7_connector import T7Connector


class SyncManager:
    def __init__(self, db_session=None):
        self.notion = NotionConnector()
        self.t7 = T7Connector()
        self.log = []
        self.db_session = db_session
        if db_session:
            from services.indexing import EntityIndexBuilder
            self.index_builder = EntityIndexBuilder(db_session)
        else:
            self.index_builder = None

    def sync(self, mode="full", table=None, identity=None):
        """Run a sync cycle. mode: 'full' or 'fast'. table: restrict to one table."""
        # Pull from Notion and T7
        notion_data = self.notion.pull(table=table)
        t7_data = self.t7.pull(table=table) if hasattr(self.t7, 'pull') else {}
        # Diff and resolve conflicts
        resolved = {}
        for t in (notion_data.keys() | t7_data.keys()):
            n_records = {r.id: r for r in notion_data.get(t, [])}
            t7_records = {r.id: r for r in t7_data.get(t, [])}
            all_ids = set(n_records.keys()) | set(t7_records.keys())
            resolved[t] = []
            for rid in all_ids:
                n = n_records.get(rid)
                t7 = t7_records.get(rid)
                # Strict timestamp-based conflict resolution
                if n and t7:
                    n_time = getattr(n, 'last_modified', None)
                    t7_time = getattr(t7, 'last_modified', None)
                    if n_time and t7_time:
                        winner = n if n_time > t7_time else t7
                    elif n_time:
                        winner = n
                    elif t7_time:
                        winner = t7
                    else:
                        winner = n  # Default to Notion if no timestamps
                else:
                    winner = n or t7
                resolved[t].append(winner)
        # Push resolved records
        for t, records in resolved.items():
            self.notion.push(records, table=t)
            if hasattr(self.t7, 'push'):
                self.t7.push(records, table=t)
        # Update entity index if available
        if self.index_builder:
            from models.entity import Entity
            for t, records in resolved.items():
                for record in records:
                    if isinstance(record, Entity):
                        self.index_builder.build_index_for_entity(record)
        self.log.append(f"Sync completed: mode={mode}, table={table}")
        # Telemetry hook
        if self.db_session:
            from services.telemetry_repository import TelemetryRepository
            TelemetryRepository.add(self.db_session, 'sync_jobs', 1, __import__('datetime').datetime.utcnow(), {'mode': mode, 'table': table})
            # Audit log
            try:
                from services.audit.service import AuditService
                job_summary = {k: len(v) for k, v in resolved.items()}
                AuditService.log(
                    self.db_session,
                    identity=identity,
                    action="sync.run",
                    target_type="system",
                    target_id="sync_engine",
                    target_label=f"mode={mode}, table={table}",
                    metadata={"job_summary": job_summary},
                    status="success",
                )
            except Exception:
                pass
        return resolved

    def diff(self, table=None):
        """Show inconsistencies between Notion and T7."""
        notion_data = self.notion.pull(table=table)
        t7_data = self.t7.pull(table=table) if hasattr(self.t7, 'pull') else {}
        return self.notion.diff(t7_data, table=table)

    def log_event(self, event):
        self.log.append(event)

    def get_log(self):
        return self.log
