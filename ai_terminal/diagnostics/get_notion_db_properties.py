
import os
import sys
import re

# Try both direct file imports for Notion API helper
get = None
notion_src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src/notion.py'))
notion_lib_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../notion/notion.py'))
import importlib.util
for path in [notion_src_path, notion_lib_path]:
    if os.path.exists(path):
        spec = importlib.util.spec_from_file_location("notion_get", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        if hasattr(mod, 'get'):
            get = mod.get
            break
if get is None:
    print("Could not import Notion API helper from src/notion.py or notion/notion.py. Check your project structure.")
    sys.exit(1)


import re

def print_db_properties(db_id):
    resp = get(f"databases/{db_id}")
    props = resp.get("properties", {})
    print(f"Properties for database {db_id}:")
    for name, prop in props.items():
        prop_type = prop.get("type", "unknown")
        print(f"- {name}: {prop_type}")

def get_db_id_from_name(name):
    env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../.env'))
    if not os.path.exists(env_path):
        print(f".env file not found at {env_path}")
        return None
    with open(env_path) as f:
        for line in f:
            m = re.match(r"NOTION_DATABASE_ID_([A-Z0-9_]+)=(\w+)", line.strip())
            if m:
                key, dbid = m.groups()
                if name.replace(' ', '').upper() in key:
                    return dbid
    return None

if __name__ == "__main__":
    user_input = input("Enter Notion database name or ID: ").strip()
    db_id = user_input
    if user_input and not re.match(r"^[a-f0-9]{32}$", user_input):
        # Try to look up by name
        db_id = get_db_id_from_name(user_input)
        if not db_id:
            print(f"Could not find database ID for name: {user_input}")
            sys.exit(1)
    if not db_id:
        print("No database ID provided.")
    else:
        print_db_properties(db_id)
