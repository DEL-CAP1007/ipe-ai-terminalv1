import os
import requests

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_ROOT_PAGE = os.getenv("NOTION_ROOT_PAGE")
NOTION_VERSION = os.getenv("NOTION_VERSION", "2025-09-03")

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": NOTION_VERSION,
    "Content-Type": "application/json"
}

# Step 1: Get data sources for the database
resp = requests.get(
    f"https://api.notion.com/v1/databases/{NOTION_ROOT_PAGE}",
    headers=headers
)
if resp.status_code != 200:
    print("Failed to fetch database info:", resp.text)
    exit(1)

db_info = resp.json()
data_sources = db_info.get("data_sources", [])
if not data_sources:
    print("No data sources found in database response.")
    exit(1)

data_source_id = data_sources[0]["id"]
print("Using data_source_id:", data_source_id)

# Step 2: Query the data source
query_url = f"https://api.notion.com/v1/data_sources/{data_source_id}/query"
query_resp = requests.patch(query_url, headers=headers, json={})
if query_resp.status_code != 200:
    print("Failed to query data source:", query_resp.text)
    exit(1)

print("Query result:", query_resp.json())
