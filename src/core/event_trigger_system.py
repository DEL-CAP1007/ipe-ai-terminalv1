
import threading
import time
from core.sync_manager import SyncManager

class EventTriggerSystem:
    def __init__(self, sync_manager: SyncManager = None, poll_interval=60):
        self.sync_manager = sync_manager or SyncManager()
        self.poll_interval = poll_interval
        self.running = False
        self.thread = None

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._poll_loop, daemon=True)
            self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()

    def _poll_loop(self):
        last_notion_hashes = {}
        last_t7_hashes = {}
        while self.running:
            print("[EventTriggerSystem] Polling for changes...")
            notion_data = self.sync_manager.notion.pull()
            t7_data = self.sync_manager.t7.pull()
            # Check for Notion changes
            for t, records in notion_data.items():
                hashes = {r.id: getattr(r, 'hash', None) for r in records}
                if t in last_notion_hashes and hashes != last_notion_hashes[t]:
                    print(f"Change detected in Notion table {t}, triggering sync.")
                    self.sync_manager.sync(table=t)
                last_notion_hashes[t] = hashes
            # Check for T7 changes
            for t, records in t7_data.items():
                hashes = {r.id: getattr(r, 'hash', None) for r in records}
                if t in last_t7_hashes and hashes != last_t7_hashes[t]:
                    print(f"Change detected in T7 table {t}, triggering sync.")
                    self.sync_manager.sync(table=t)
                last_t7_hashes[t] = hashes
            time.sleep(self.poll_interval)

# Usage example:
# from core.sync_manager import SyncManager
# sync_manager = SyncManager(...)
# event_trigger = EventTriggerSystem(sync_manager, poll_interval=60)
# event_trigger.start()
