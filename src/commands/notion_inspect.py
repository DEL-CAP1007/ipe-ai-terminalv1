import requests
from commands.notion import BASE_URL, headers

def list_all_databases():
    """
    Lists all Notion databases accessible with the current integration token,
    including:
    - Title
    - Database ID
    - Number of properties
    - Last edited time
    """

    print("\n=== LISTING ALL NOTION DATABASES ===\n")

    url = f"{BASE_URL}/search"

    payload = {
        "filter": {"value": "database", "property": "object"},
        "page_size": 100
    }

    try:
        resp = requests.post(url, headers=headers, json=payload)
        data = resp.json()

        results = data.get("results", [])
        if not results:
            print("No databases found. Check integration permissions.")
            return

        for db in results:
            title = db.get("title", [])
            db_name = title[0]["plain_text"] if title else "(Untitled Database)"
            db_id = db.get("id")
            last_edited = db.get("last_edited_time")

            properties = db.get("properties", {})
            prop_count = len(properties)

            print(f"\U0001F4D8 DATABASE: {db_name}")
            print(f"    ID: {db_id}")
            print(f"    Properties: {prop_count}")
            print(f"    Last Edited: {last_edited}")
            print("-" * 70)

        print("\n=== END OF DATABASE LIST ===\n")

    except Exception as e:
        print(f"[ERROR] Failed to list databases: {e}")
