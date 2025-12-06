
import os
import sys
import time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from ai_terminal.utils.load_env import load_env
from notion.notion import get

PAGE_IDS = [
    "2bc9333e656d806c90c4e073c875c381",  # OS Command Centers
    "2bc9333e656d80ae826eeac554a69e4e",  # Master Databases
    "2bc9333e656d800d9013f5e786799dfa",  # Dashboards
    "2bc9333e656d805fac56ed73f9f890a2",  # System Documentation
    "2bc9333e656d80adb2dada9b6b86e821",  # Archive - System Tests & Backups
    "2bb9333e656d8129ac7ad6c28861d9fa",  # IPE Tasks Master Timeline
]

load_env()
NOTION_TOKEN = os.getenv("NOTION_API_KEY") or os.getenv("NOTION_TOKEN")
if not NOTION_TOKEN:
    raise SystemExit("No Notion token found in environment.")

for page_id in PAGE_IDS:
    print(f"\nTesting access to page: {page_id}")
    os.environ["NOTION_ROOT_PAGE"] = page_id
    root = get(f"pages/{page_id}")
    if "object" in root and root["object"] == "error":
        print("[X] Cannot access root page.")
        print(root)
    else:
        print("[OK] Root page accessible.")
