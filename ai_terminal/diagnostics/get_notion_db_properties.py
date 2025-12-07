import os
from notion.notion import get

def print_db_properties(db_id):
    resp = get(f"databases/{db_id}")
    props = resp.get("properties", {})
    print(f"Properties for database {db_id}:")
    for name, prop in props.items():
        prop_type = prop.get("type", "unknown")
        print(f"- {name}: {prop_type}")

if __name__ == "__main__":
    db_id = input("Enter Notion database ID: ").strip()
    if not db_id:
        print("No database ID provided.")
    else:
        print_db_properties(db_id)
