
import os
from core.normalization import CanonicalRecord, normalize_notion_record
import requests

class NotionConnector:
    def __init__(self):
        self.api_key = os.getenv("NOTION_API_KEY") or os.getenv("NOTION_TOKEN")
        self.version = os.getenv("NOTION_VERSION", "2022-06-28")
        self.db_ids = self._get_db_ids()

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Notion-Version": self.version,
            "Content-Type": "application/json"
        }

    def _get_db_ids(self):
        # Load all NOTION_DATABASE_ID_* from .env
        db_ids = {}
        env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../.env'))
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    if line.startswith("NOTION_DATABASE_ID_"):
                        key, dbid = line.strip().split("=")
                        db_ids[key.replace("NOTION_DATABASE_ID_", "").lower()] = dbid
        return db_ids

    def pull(self, table=None):
        """Fetch data from Notion. If table is None, fetch all."""
        results = {}
        tables = [table] if table else self.db_ids.keys()
        for t in tables:
            db_id = self.db_ids.get(t.lower())
            if not db_id:
                continue
            url = f"https://api.notion.com/v1/databases/{db_id}/query"
            resp = requests.post(url, headers=self._headers(), json={})
            data = resp.json().get("results", [])
            results[t] = [normalize_notion_record(r) for r in data]
        return results

    def push(self, records, table=None):
        """Push data to Notion. records: list of CanonicalRecord."""
        # For demo, just print what would be pushed
        print(f"Would push {len(records)} records to Notion table {table}")
        # Implement actual Notion API update/create logic here

    def diff(self, local_records, table=None):
        """Compare Notion data with local records. Returns diff report."""
        notion_data = self.pull(table=table)
        diffs = {}
        for t, notion_records in notion_data.items():
            local = local_records.get(t, []) if local_records else []
            notion_ids = {r.id for r in notion_records}
            local_ids = {r.id for r in local}
            only_in_notion = notion_ids - local_ids
            only_in_local = local_ids - notion_ids
            diffs[t] = {
                "only_in_notion": list(only_in_notion),
                "only_in_local": list(only_in_local)
            }
        return diffs

    def subscribe(self, callback):
        """Subscribe to Notion changes (polling). Calls callback on change."""
        # For demo, implement simple polling loop (not production-ready)
        import time
        last_hashes = {}
        while True:
            notion_data = self.pull()
            for t, records in notion_data.items():
                hashes = {r.id: r.hash for r in records}
                if t in last_hashes and hashes != last_hashes[t]:
                    callback(t, records)
                last_hashes[t] = hashes
            time.sleep(60)  # Poll every 60 seconds
