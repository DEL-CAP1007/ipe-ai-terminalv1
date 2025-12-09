
import os
import json
from core.normalization import CanonicalRecord, normalize_t7_record

class T7Connector:
    def __init__(self):
        self.state_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../t7_state'))
        os.makedirs(self.state_dir, exist_ok=True)

    def _get_table_path(self, table):
        return os.path.join(self.state_dir, f'{table}.json')

    def pull(self, table=None):
        """Fetch data from T7 local DB/state. If table is None, fetch all."""
        results = {}
        tables = [table] if table else self._list_tables()
        for t in tables:
            path = self._get_table_path(t)
            if os.path.exists(path):
                with open(path) as f:
                    data = json.load(f)
                results[t] = [normalize_t7_record(r) for r in data]
            else:
                results[t] = []
        return results

    def push(self, records, table=None):
        """Push data to T7 local DB/state. records: list of CanonicalRecord."""
        if not table:
            print("Table name required for T7 push.")
            return
        path = self._get_table_path(table)
        data = [r.__dict__ for r in records]
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Pushed {len(records)} records to T7 table {table}")

    def diff(self, remote_records, table=None):
        """Compare T7 data with remote records. Returns diff report."""
        t7_data = self.pull(table=table)
        diffs = {}
        for t, t7_records in t7_data.items():
            remote = remote_records.get(t, []) if remote_records else []
            t7_ids = {r.id for r in t7_records}
            remote_ids = {r.id for r in remote}
            only_in_t7 = t7_ids - remote_ids
            only_in_remote = remote_ids - t7_ids
            diffs[t] = {
                "only_in_t7": list(only_in_t7),
                "only_in_remote": list(only_in_remote)
            }
        return diffs

    def subscribe(self, callback):
        """Subscribe to T7 changes (polling). Calls callback on change."""
        import time
        last_hashes = {}
        while True:
            t7_data = self.pull()
            for t, records in t7_data.items():
                hashes = {r.id: r.hash for r in records}
                if t in last_hashes and hashes != last_hashes[t]:
                    callback(t, records)
                last_hashes[t] = hashes
            time.sleep(60)  # Poll every 60 seconds

    def _list_tables(self):
        return [f[:-5] for f in os.listdir(self.state_dir) if f.endswith('.json')]
