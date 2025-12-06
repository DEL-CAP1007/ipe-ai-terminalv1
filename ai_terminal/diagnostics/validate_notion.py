from dotenv import load_dotenv
import os
import requests

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
ROOT_PAGE = os.getenv("NOTION_ROOT_PAGE")
NOTION_VERSION = os.getenv("NOTION_VERSION", "2025-09-03")

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": NOTION_VERSION
}


def check_token():
    print("\n[1] Checking Notion token…")
    if NOTION_TOKEN and len(NOTION_TOKEN) > 40:
        # Try a simple API call to validate token
        url = "https://api.notion.com/v1/users/me"
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            print("   [√] Token is valid and accepted by Notion API")
            return True
        else:
            print(f"   [X] Token rejected by Notion API: {resp.text}")
            return False
    print("   [X] Token missing or invalid format")
    return False

def check_root_access():
    print("\n[2] Checking Root Page access…")
    url = f"https://api.notion.com/v1/pages/{ROOT_PAGE}"
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        print("   [√] Root page accessible")
        return True
    print("   [X] Cannot access Root page:", resp.text)
    return False

def list_databases():
    print("\n[3] Searching for master databases…")
    url = "https://api.notion.com/v1/search"
    payload = {
        "query": "",
        "filter": {"value": "database", "property": "object"}
    }
    resp = requests.post(url, headers=headers, json=payload)
    data = resp.json()

    found = []
    for db in data.get("results", []):
        title = db.get("title", [{}])[0].get("plain_text", "")
        found.append((title, db.get("id")))

    return found

REQUIRED_DATABASES = [
    "IPE Tasks (Master)",
    "IPE Events (Master)",
    "IPE Clients (Master)",
    "K-12 Indigenous Programs (Master)",
    "Speakers & Facilitators (Master)",
    "IndigiRise Cohorts (Master)",
    "IndigiRise Participants (Master)",
    "IPE Communication Log (Master)"
]

def validate_required_databases(found):
    print("\n[4] Validating required master databases…")
    names = [f[0] for f in found]
    all_good = True

    for req in REQUIRED_DATABASES:
        if req in names:
            print(f"   [√] {req} found")
        else:
            print(f"   [X] {req} MISSING")
            all_good = False
    return all_good

def test_page_create_update_delete():
    print("\n[5] Testing page create → update → delete…")

    # Create
    create_url = "https://api.notion.com/v1/pages"
    payload = {
        "parent": {"page_id": ROOT_PAGE},
        "properties": {
            "title": [{"type": "text", "text": {"content": "TEST PAGE"}}]
        }
    }
    create_resp = requests.post(create_url, headers=headers, json=payload)

    if create_resp.status_code not in [200, 201]:
        print("   [X] Failed to create page:", create_resp.text)
        return False

    page_id = create_resp.json()["id"]
    print("   [√] Created test page")

    # Update
    update_url = f"https://api.notion.com/v1/pages/{page_id}"
    update_resp = requests.patch(update_url, headers=headers, json={
        "properties": {
            "title": [{"type": "text", "text": {"content": "TEST PAGE UPDATED"}}]
        }
    })
    if update_resp.status_code != 200:
        print("   [X] Failed to update page:", update_resp.text)
        return False

    print("   [√] Updated test page")

    # Delete (archive)
    delete_resp = requests.patch(update_url, headers=headers, json={"archived": True})
    if delete_resp.status_code == 200:
        print("   [√] Archived (deleted) test page")
        return True

    print("   [X] Failed to delete test page:", delete_resp.text)
    return False


def run_full_validation():
    print("\n====================================")
    print("      IPE ENTERPRISE OS VALIDATION")
    print("====================================")

    ok = True
    ok &= check_token()
    ok &= check_root_access()

    print("\n====================================")
    if ok:
        print("SYSTEM STATUS: TOKEN AND ROOT PAGE ACCESS OK")
    else:
        print("SYSTEM STATUS: ISSUES DETECTED")
    print("====================================")

if __name__ == "__main__":
    run_full_validation()
