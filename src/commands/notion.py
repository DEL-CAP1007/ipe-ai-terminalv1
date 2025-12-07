import os
import json
import time
import requests
from pathlib import Path
from core.llm import ask_ai
from commands.filesystem import sync_folder, CLOUD_ROOT, create_onboarding_folders, create_speaker_folders, create_k12_folders, create_event_folders
from commands.notion_helpers import update_folder_path
def update_page_content(page_id, new_content, dry_run=False):
    """
    Replace the content blocks of a Notion page with new_content (as paragraphs).
    """
    url = f"{BASE_URL}/blocks/{page_id}/children"

    # Break new_content into paragraph blocks
    def _chunks_from_text(text, max_len=1900):
        paras = [p.strip() for p in text.split("\n\n") if p.strip()]
        chunks = []
        for p in paras:
            if len(p) <= max_len:
                chunks.append(p)
            else:
                import textwrap
                parts = textwrap.wrap(p, width=max_len, break_long_words=False, replace_whitespace=False)
                for part in parts:
                    if part.strip():
                        chunks.append(part)
        if not chunks and text.strip():
            chunks = [text.strip()]
        return chunks

    children = []
    for chunk in _chunks_from_text(new_content):
        children.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {"type": "text", "text": {"content": chunk}}
                ]
            }
        })

    data = {"children": children}

    if dry_run:
        print("DRY-RUN: would PATCH to:", url)
        print(json.dumps(data, indent=2))
        return

    try:
        resp = _request_with_retries("PATCH", url, headers=headers, json=data)
    except Exception as exc:
        print("Error updating page content:", exc)
        return None

    _save_last_response(resp)
    if 200 <= resp.status_code < 300:
        print("\n==== PAGE CONTENT UPDATED ====")
        try:
            print(resp.json())
        except Exception:
            print(resp.text)
        return resp
    else:
        print("\n==== NOTION ERROR (update content) ====")
        try:
            print(resp.json())
        except Exception:
            print(resp.text)
        return resp
def get_database_by_name(database_name):
    """
    Fetches the full database object from Notion by name.
    """
    db_id = get_database_id(database_name)
    if not db_id:
        return None
    url = f"{BASE_URL}/databases/{db_id}"
    try:
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        print(f"[ERROR] Could not fetch database: {e}")
    return None


def debug_properties(database_name):
    """
    Prints all properties for the given database and their exact types,
    as returned by the Notion API.
    """
    print(f"\n=== Debug: Properties for Database '{database_name}' ===\n")

    db = get_database_by_name(database_name)

    if not db:
        print("[ERROR] Database not found.")
        return

    props = db["properties"]

    for prop_name, prop_data in props.items():
        prop_type = prop_data.get("type", "UNKNOWN")
        print(f"- {prop_name} : {prop_type}")

    print("\n=== End Debug ===\n")
# --- Schedule Engine Helper ---
def create_task(task_name, parent_page_id, timeline_start=None, timeline_end=None):
    """Create a Notion task as a database entry in IPE Tasks and return its page ID.
    Accepts parent_page_id (unused), and optionally timeline_start/timeline_end as datetime objects."""
    db_id = get_database_id("IPE Tasks")
    if not db_id:
        print("[Notion] IPE Tasks database not found.")
        return None
    url = f"{BASE_URL}/pages"
    properties = {
        "Name": {"title": [{"type": "text", "text": {"content": task_name}}]},
        "Status": {"select": {"name": "Not Started"}},
        "Priority": {"select": {"name": "Medium"}},
        "Category": {"select": {"name": "Event"}},
        "Notes": {"rich_text": [{"type": "text", "text": {"content": ""}}]},
        "Timeline Start": {"date": {"start": timeline_start.strftime("%Y-%m-%d") if timeline_start and hasattr(timeline_start, 'strftime') else str(timeline_start) if timeline_start else None}},
        "Timeline End": {"date": {"start": timeline_end.strftime("%Y-%m-%d") if timeline_end and hasattr(timeline_end, 'strftime') else str(timeline_end) if timeline_end else None}},
        "Duration Days": {"number": 0},
        "Assigned To": {"people": []},
        "Critical Task": {"checkbox": False},
        "Folder Path": {"url": ""},
        "Cloud Folder": {"url": ""},
        "Program Type": {"select": {"name": "IndigiRise Accelerator"}},
        "Event Type": {"select": {"name": "Pitch Night"}}
        # Relations (Parent Event, Parent Program, Parent Cohort, Client, Speaker / Facilitator, Participant) can be added here if IDs are available
    }
    # Relations: Add as needed, e.g.:
    # properties["Parent Event"] = {"relation": [{"id": parent_event_id}]}
    # properties["Parent Program"] = {"relation": [{"id": parent_program_id}]}
    # ...
    data = {
        "parent": {"type": "database_id", "database_id": db_id},
        "properties": properties
    }
    try:
        resp = _request_with_retries("POST", url, headers=headers, json=data)
    except Exception as exc:
        print("Error creating database task:", exc)
        return None
    if 200 <= resp.status_code < 300:
        try:
            return resp.json().get('id')
        except Exception:
            return None
    else:
        print("[Notion] Failed to create database task:")
        try:
            print(resp.json())
        except Exception:
            print(resp.text)
        return None

NOTION_VERSION = "2022-06-28"
BASE_URL = "https://api.notion.com/v1"
NOTION_ROOT_PAGE = os.environ.get("NOTION_ROOT_PAGE", "YOUR_ROOT_PAGE_ID")
NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "YOUR_NOTION_TOKEN")
headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": NOTION_VERSION
}
LOG_DIR = Path(__file__).parent.parent.parent / "notion"

# --- Notion property update helper ---
def update_page_property(page_id, property_name, value):
    """Update a property on a Notion page."""
    url = f"{BASE_URL}/pages/{page_id}"
    # Always fetch property type from the schema
    prop_type = None
    try:
        db_id = get_database_id("IPE Tasks")
        url = f"{BASE_URL}/databases/{db_id}"
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            schema = resp.json().get("properties", {})
            if property_name in schema:
                prop_type = schema[property_name].get("type")
    except Exception:
        pass

    if prop_type == "date":
        data = {
            "properties": {
                property_name: {
                    "date": {"start": value}
                }
            }
        }
    elif prop_type == "url":
        data = {
            "properties": {
                property_name: {
                    "url": value
                }
            }
        }
    else:
        data = {
            "properties": {
                property_name: {
                    "rich_text": [{"text": {"content": value}}]
                }
            }
        }
    try:
        resp = _request_with_retries("PATCH", url, headers=headers, json=data)
        if 200 <= resp.status_code < 300:
            print(f"[Notion] Updated property '{property_name}' for page {page_id}")
        else:
            print(f"[Notion] Failed to update property '{property_name}' for page {page_id}")
            try:
                print("[Notion] Response:", resp.json())
            except Exception:
                print("[Notion] Response (raw):", resp.text)
    except Exception as e:
        print(f"[Notion] Error updating property: {e}")
def generate_k12(program_title):
    folder_path = create_k12_folders(program_title)
    content = f"K12 Program: {program_title}"
    resp = create_page(f"K12 Program: {program_title}", content)
    page_id = None
    if resp and hasattr(resp, 'json'):
        try:
            page_id = resp.json().get('id')
        except Exception:
            pass
    if page_id:
        update_folder_path(page_id, folder_path)
        # Cloud sync
        import os
        cloud_path = os.path.join(CLOUD_ROOT, "K12", program_title)
        sync_folder(folder_path, cloud_path)
        update_page_property(page_id, "Cloud Folder", f"file://{cloud_path}")
    print(f"[STUB] Would generate K12 program: {program_title}")

def generate_event(event_title):
    print(f"[STUB] Would generate event: {event_title}")

def test_system():
    print("[STUB] System test would run here.")

def generate_tasks(project_title):
    # --- Minimal stub for CLI routing ---
    pass

def generate_onboarding(client_name):
    """Generates a full onboarding page for a client or program."""
    folder_path = create_onboarding_folders(client_name)
    content = f"Onboarding for {client_name}"
    resp = create_page(f"Onboarding: {client_name}", content)
    page_id = None
    if resp and hasattr(resp, 'json'):
        try:
            page_id = resp.json().get('id')
        except Exception:
            pass
    if page_id:
        update_folder_path(page_id, folder_path)
        # Cloud sync
        import os
        cloud_path = os.path.join(CLOUD_ROOT, "Onboarding", client_name)
        sync_folder(folder_path, cloud_path)
        update_page_property(page_id, "Cloud Folder", f"file://{cloud_path}")

 # --- CLI Routing ---
def run_notion(args):
    if action == "setup-comm-log-properties":
        db_name = "IPE Communication Log (Master)"
        # 1. Assigned To
        add_property(db_name, "Assigned To", "person")
        # 2. Attachment
        add_property(db_name, "Attachment", "files")
        # 3. Communication Category
        add_property(db_name, "Communication Category", "select")
        # 4. Date
        add_property(db_name, "Date", "date")
        # 5. Interaction Type
        add_property(db_name, "Interaction Type", "select")
        # 6. Source Platform
        add_property(db_name, "Source Platform", "select")
        # 7. Summary / Notes
        add_property(db_name, "Summary / Notes", "rich_text")
        # 8. Next Step / Action Required
        add_property(db_name, "Next Step / Action Required", "rich_text")
        # 9. Time Logged
        add_property(db_name, "Time Logged", "number")
        # 10. Related Event (relation)
        add_relation_property(db_name, "Related Event", "IPE Events (Master)")
        # 11. Related Client (relation)
        add_relation_property(db_name, "Related Client", "IPE Clients (Master)")
        # 12. Cohorts (relation)
        add_relation_property(db_name, "Cohorts", "IndigiRise Cohorts (Master)")
        # 13. Participants (relation)
        add_relation_property(db_name, "Participants", "IndigiRise Participants (Master)")
        # 14. Programs (relation)
        add_relation_property(db_name, "Programs", "K–12 Indigenous Programs (Master)")
        # 15. Speakers & Facilitators (relation)
        add_relation_property(db_name, "Speakers & Facilitators", "Speakers & Facilitators (Master)")
        print("All properties for IPE Communication Log (Master) added. Add reverse relations manually in Notion UI if needed.")
        return
    if action == "setup-speakers-properties":
        db_name = "Speakers & Facilitators (Master)"
        # 1. Name (title)
        # 2. Email
        add_property(db_name, "Email", "email")
        # 3. Phone
        add_property(db_name, "Phone", "phone")
        # 4. Region
        add_property(db_name, "Region", "select")
        # 5. Nation / Community
        add_property(db_name, "Nation / Community", "rich_text")
        # 6. Role
        add_property(db_name, "Role", "select")
        # 7. Type
        add_property(db_name, "Type", "select")
        # 8. Category
        add_property(db_name, "Category", "select")
        # 9. Biography
        add_property(db_name, "Biography", "rich_text")
        # 10. Photo
        add_property(db_name, "Photo", "files")
        # 11. Media Release on File?
        add_property(db_name, "Media Release on File?", "checkbox")
        # 12. Cultural Protocol Notes
        add_property(db_name, "Cultural Protocol Notes", "rich_text")
        # 13. Certifications
        add_property(db_name, "Certifications", "rich_text")
        # 14. Availability
        add_property(db_name, "Availability", "rich_text")
        # 15. Day Rate
        add_property(db_name, "Day Rate", "number")
        # 16. Session Rate
        add_property(db_name, "Session Rate", "number")
        # 17. Honoraria Provided
        add_property(db_name, "Honoraria Provided", "checkbox")
        # 18. Travel Requirements
        add_property(db_name, "Travel Requirements", "rich_text")
        # 19. Folder Path
        add_property(db_name, "Folder Path", "url")
        # 20. Cloud Folder
        add_property(db_name, "Cloud Folder", "url")
        # 21. Clients (relation)
        add_relation_property(db_name, "Clients", "IPE Clients (Master)")
        # 22. Programs (relation)
        add_relation_property(db_name, "Programs", "K–12 Indigenous Programs (Master)")
        # 23. Events (relation)
        add_relation_property(db_name, "Events", "IPE Events (Master)")
        # 24. Tasks (relation)
        add_relation_property(db_name, "Tasks", "IPE Tasks (Master)")
        # 25. Communication Log (relation)
        add_relation_property(db_name, "Communication Log", "IPE Communication Log (Master)")
        print("All properties for Speakers & Facilitators (Master) added. Add reverse relations manually in Notion UI if needed.")
        return
        if action == "setup-speakers-properties":
            db_name = "Speakers & Facilitators (Master)"
            # 1. Name (title)
            # 2. Biography
            add_property(db_name, "Biography", "text")
            # 3. Indigenous Identity & Background
            add_property(db_name, "Indigenous Identity & Background", "text")
            # 4. Areas of Expertise
            add_property(db_name, "Areas of Expertise", "multi_select")
            # 5. Speaking Topics
            add_property(db_name, "Speaking Topics", "multi_select")
            # 6. Cultural Knowledge & Teachings
            add_property(db_name, "Cultural Knowledge & Teachings", "text")
            # 7. Workshop / Program Offerings
            add_property(db_name, "Workshop / Program Offerings", "text")
            # 8. Availability
            add_property(db_name, "Availability", "text")
            # 9. Travel Requirements
            add_property(db_name, "Travel Requirements", "text")
            # 10. Contact Info
            add_property(db_name, "Contact Info", "text")
            # 11. Fees
            add_property(db_name, "Fees", "text")
            # 12. Media Assets
            add_property(db_name, "Media Assets", "files")
            # 13. Additional Notes
            add_property(db_name, "Additional Notes", "text")
            print("All required and optional properties for Speakers & Facilitators (Master) added. Add relations manually in Notion UI.")
            return
    if not args:
        print("Missing Notion action.")
        return
    action = args[0]
    if action == "setup-clients-properties":
        db_name = "IPE Clients (Master)"
        # 1. Name (title)
        # 2. Email
        add_property(db_name, "Email", "email")
        # 3. Phone Number
        add_property(db_name, "Phone Number", "phone")
        # 4. Status
        add_property(db_name, "Status", "status")
        # 5. Program Type
        add_property(db_name, "Program Type", "select")
        # 6. Folder Path
        add_property(db_name, "Folder Path", "text")
        # 7. Cloud Folder
        add_property(db_name, "Cloud Folder", "text")
        # 8. Notes
        add_property(db_name, "Notes", "text")
        # 9. Photo
        add_property(db_name, "Photo", "files")
        # 10. Application Form Link
        add_property(db_name, "Application Form Link", "url")
        # 11. Progress Score (Internal)
        add_property(db_name, "Progress Score (Internal)", "number")
        # 12. Pitch Readiness Level
        add_property(db_name, "Pitch Readiness Level", "select")
        print("All required and optional properties for IPE Clients (Master) added. Add relations manually in Notion UI.")
        return
    if not args:
        print("Missing Notion action.")
        return
    action = args[0]
    if action == "setup-comm-log-properties":
        db_name = "IPE Communication Log (Master)"
        # 1. Date
        add_property(db_name, "Date", "date")
        # 2. Interaction Type
        add_property(db_name, "Interaction Type", "select")
        # Add select options for Interaction Type
        # 3. Summary / Notes
        add_property(db_name, "Summary / Notes", "text")
        # 4. Next Step / Action Required
        add_property(db_name, "Next Step / Action Required", "text")
        # 5. Assigned To
        add_property(db_name, "Assigned To", "person")
        # 6. Related Event
        add_relation_property(db_name, "Related Event", "IPE Events (Master)")
        # 7. Related Client
        add_relation_property(db_name, "Related Client", "IPE Clients (Master)")
        # 8. Related Task
        add_relation_property(db_name, "Related Task", "IPE Tasks (Master)")
        # 9. Communication Category
        add_property(db_name, "Communication Category", "select")
        # 10. Attachment
        add_property(db_name, "Attachment", "files")
        # 11. Source Platform
        add_property(db_name, "Source Platform", "select")
        # 12. Time Logged
        add_property(db_name, "Time Logged", "number")
        print("All required properties for Communication Log added.")
        return
    if action == "setup-cohorts-properties":
        db_name = "IndigiRise Cohorts (Master)"
        # 1. Status
        add_property(db_name, "Status", "select")
        # 2. Program Type
        add_property(db_name, "Program Type", "select")
        # 3. Start Date
        add_property(db_name, "Start Date", "date")
        # 4. End Date
        add_property(db_name, "End Date", "date")
        # 5. Notes
        add_property(db_name, "Notes", "rich_text")
        # 6. Folder Path
        add_property(db_name, "Folder Path", "url")
        # 7. Cloud Folder
        add_property(db_name, "Cloud Folder", "url")
        # 8. Participants (relation)
        add_relation_property(db_name, "Participants", "IndigiRise Participants (Master)")
        # 9. Events (relation)
        add_relation_property(db_name, "Events", "IPE Events (Master)")
        # 10. Tasks (relation)
        add_relation_property(db_name, "Tasks", "IPE Tasks (Master)")
        # 11. Communication Log (relation)
        add_relation_property(db_name, "Communication Log", "IPE Communication Log (Master)")
        print("All properties for IndigiRise Cohorts (Master) added. Add formulas manually in Notion UI if needed.")
        return
    if not args:
        print("Missing Notion action.")
        return
    action = args[0]
    if action == "setup-comm-log-properties":
        db_name = "IPE Communication Log (Master)"
        # 1. Date
        add_property(db_name, "Date", "date")
        # 2. Interaction Type
        add_property(db_name, "Interaction Type", "select")
        # Add select options for Interaction Type
        # 3. Summary / Notes
        add_property(db_name, "Summary / Notes", "text")
        # 4. Next Step / Action Required
        add_property(db_name, "Next Step / Action Required", "text")
        # 5. Assigned To
        add_property(db_name, "Assigned To", "person")
        # 6. Related Event
        add_relation_property(db_name, "Related Event", "IPE Events (Master)")
        # 7. Related Client
        add_relation_property(db_name, "Related Client", "IPE Clients (Master)")
        # 8. Related Task
        add_relation_property(db_name, "Related Task", "IPE Tasks (Master)")
        # 9. Communication Category
        add_property(db_name, "Communication Category", "select")
        # 10. Attachment
        add_property(db_name, "Attachment", "files")
        # 11. Source Platform
        add_property(db_name, "Source Platform", "select")
        # 12. Time Logged
        add_property(db_name, "Time Logged", "number")
        print("All required properties for Communication Log added.")
        return
    if action == "setup-cohorts-properties":
        db_name = "IndigiRise Cohorts (Master)"
        # 1. Name (already present as title)
        # 2. Status
        add_property(db_name, "Status", "status")
        # 3. Start Date
        add_property(db_name, "Start Date", "date")
        # 4. End Date
        add_property(db_name, "End Date", "date")
        # 5. Duration (Days) - Formula
        # Notion API does not support formulas directly; must be added manually in UI
        # 6. Program Type
        add_property(db_name, "Program Type", "select")
        # 7. Parent Event
        # Must be added manually in UI (relation)
        # 8. Participants
        # Must be added manually in UI (relation)
        # 9. Tasks (Cohort-Level)
        # Must be added manually in UI (relation)
        # 10. Communication Log
        # Must be added manually in UI (relation)
        # 11. Folder Path
        add_property(db_name, "Folder Path", "text")
        # 12. Cloud Folder
        add_property(db_name, "Cloud Folder", "text")
        # 13. Notes
        add_property(db_name, "Notes", "text")
        print("All required properties for IndigiRise Cohorts (Master) added. Add relations and formula manually in Notion UI.")
        return
        if len(args) < 2:
            print("Usage: notion print-schema <db_name>")
            return
        db_name = args[1]
        db_id = get_database_id(db_name)
        if not db_id:
            print(f"Database '{db_name}' not found.")
            return
        url = f"{BASE_URL}/databases/{db_id}"
        resp = requests.get(url, headers=headers)
        if resp.status_code != 200:
            print(f"Failed to fetch schema: {resp.status_code}")
            print(resp.text)
            return
        data = resp.json()
        print(json.dumps(data.get("properties", {}), indent=2))
        return
    dry_run = False
    if "--dry-run" in args:
        dry_run = True
        args = [a for a in args if a != "--dry-run"]

    if action == "create-database":
        name = " ".join(args[1:])
        create_database(name, dry_run=dry_run)
    elif action == "add-property":
        if len(args) < 4:
            print("Usage: notion add-property <db_name> <prop_name> <prop_type> [--dry-run]")
            return
        db_name = args[1]
        prop_name = args[2]
        prop_type = args[3]
        add_property(db_name, prop_name, prop_type, dry_run=dry_run)
    elif action == "remove-property":
        if len(args) < 3:
            print("Usage: notion remove-property <db_name> <prop_name> [--dry-run]")
            return
        db_name = args[1]
        prop_name = args[2]
        remove_property(db_name, prop_name, dry_run=dry_run)
    elif action == "create-page":
        if len(args) < 3:
            print("Usage: notion create-page <title> <content>")
            return
        title = args[1]
        content = " ".join(args[2:])
        create_page(title, content)
    elif action == "generate-template":
        if len(args) < 3:
            print("Usage: notion generate-template <template_path> <title>")
            return
        template_path = args[1]
        title = args[2]
        variables = {}
        create_template_page(template_path, title, variables)
    elif action == "generate-ai-template":
        if len(args) < 4:
            print("Usage: notion generate-ai-template <template_path> <title> <prompt>")
            return
        template_path = args[1]
        title = args[2]
        prompt = " ".join(args[3:])
        generate_ai_filled_template(template_path, title, prompt)
    elif action == "generate-proposal":
        if len(args) < 2:
            print("Usage: notion generate-proposal <event_name>")
            return
        event_name = " ".join(args[1:])
        generate_proposal(event_name)
    elif action == "generate-speaker":
        if len(args) < 2:
            print("Usage: notion generate-speaker <speaker_name>")
            return
        speaker_name = " ".join(args[1:])
        generate_speaker_profile(speaker_name)
    elif action == "generate-lesson":
        if len(args) < 2:
            print("Usage: notion generate-lesson <lesson_title>")
            return
        lesson_title = " ".join(args[1:])
        generate_lesson(lesson_title)
    elif action == "generate-k12":
        if len(args) < 2:
            print("Usage: notion generate-k12 <program_title>")
            return
        program_title = " ".join(args[1:])
        generate_k12(program_title)
    elif action == "generate-event":
        if len(args) < 2:
            print("Usage: notion generate-event <event_title>")
            return
        event_title = " ".join(args[1:])
        generate_event(event_title)
    elif action == "generate-onboarding":
        if len(args) < 2:
            print("Usage: notion generate-onboarding <client_name>")
            return
        client_name = " ".join(args[1:])
        generate_onboarding(client_name)
    elif action == "generate-tasks":
        if len(args) < 2:
            print("Usage: notion generate-tasks <project_title>")
            return
        project_title = " ".join(args[1:])
        generate_tasks(project_title)
    elif action == "generate-event-bundle":
        if len(args) < 2:
            print("Usage: notion generate-event-bundle <event_title>")
            return
        event_title = " ".join(args[1:])
        generate_event_bundle(event_title)
    elif action == "install-ipe-machine":
        install_ipe_machine()
    elif action == "add-relation":
        if len(args) < 4:
            print("Usage: notion add-relation <source_db> <prop_name> <target_db>")
            return
        source = args[1]
        prop_name = args[2]
        target = args[3]
        add_relation_property(source, prop_name, target)
    elif action == "wire-ipe-relations":
        wire_ipe_relations()
    elif action == "test-system":
        test_system()
    else:
        print(f"Unknown Notion action: {action}")
def remove_property(db_name, prop_name, dry_run=False):
    """Removes a property from a Notion database by name."""
    db_id = get_database_id(db_name)
    if not db_id:
        print(f"Database '{db_name}' not found.")
        return
    url = f"{BASE_URL}/databases/{db_id}"
    # Notion API: To remove a property, set its value to null in the PATCH body
    data = {"properties": {prop_name: None}}
    if dry_run:
        print("DRY-RUN: would PATCH to:", url)
        print(json.dumps(data, indent=2))
        return
    try:
        resp = _request_with_retries("PATCH", url, headers=headers, json=data)
    except Exception as e:
        print("Error removing property:", e)
        return
    _save_last_response(resp)
    print("\n==== PROPERTY REMOVED ====")
    try:
        print(resp.json())
    except Exception:
        print(resp.text)
    # ...existing code...

LOG_DIR = Path(__file__).parent.parent.parent / "notion"
LAST_RESPONSE_PATH = LOG_DIR / "last_response.json"


def _ensure_log_dir():
    """Create log directory if it does not exist."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)


def _request_with_retries(method, url, headers=None, json=None, max_attempts=3, backoff=1):
    attempt = 0
    while attempt < max_attempts:
        try:
            resp = requests.request(method, url, headers=headers, json=json, timeout=20)
        except requests.RequestException:
            attempt += 1
            if attempt >= max_attempts:
                raise
            time.sleep(backoff * attempt)
            continue

        if 200 <= resp.status_code < 300:
            return resp

        # For 4xx errors do not retry except 429 (rate limit)
        if resp.status_code == 429:
            attempt += 1
            time.sleep(backoff * attempt)
            continue

        # other non-retriable error
        return resp






def create_database(name, dry_run=False):
    url = f"{BASE_URL}/databases"

    data = {
        "parent": {"type": "page_id", "page_id": NOTION_ROOT_PAGE},
        "title": [{"type": "text", "text": {"content": name}}],
        "properties": {"Name": {"title": {}}}
    }

    if dry_run:
        print("DRY-RUN: would POST to:", url)
        print(json.dumps(data, indent=2))
        return None

    resp = _request_with_retries("POST", url, headers=headers, json=data)
    _save_last_response(resp)
    print("\n==== NOTION RESPONSE ====")
    try:
        print(resp.json())
    except Exception:
        print(resp.text)
    return resp


def get_database_id(db_name):
    """Searches for a database by title and returns its ID (or None)."""
    url = f"{BASE_URL}/search"

    payload = {"query": db_name, "filter": {"value": "database", "property": "object"}}

    try:
        resp = _request_with_retries("POST", url, headers=headers, json=payload)
    except Exception as e:
        print("Error searching for database:", e)
        return None

    try:
        r = resp.json()
    except Exception:
        print("Invalid JSON response from Notion search")
        return None

    for result in r.get("results", []):
        # Notion search responses differ; try to be defensive
        title = ""
        if isinstance(result.get("title"), list) and result.get("title"):
            title = result.get("title")[0].get("text", {}).get("content", "")
        else:
            # fallback: look for Name property
            name_prop = result.get("properties", {}).get("Name")
            if name_prop and isinstance(name_prop.get("title"), list) and name_prop.get("title"):
                title = name_prop.get("title")[0].get("plain_text", "")

        if title and title.lower() == db_name.lower():
            return result.get("id")

    return None


def add_property(db_name, prop_name, prop_type, dry_run=False):
    # find DB id
    db_id = get_database_id(db_name)

    if not db_id:
        print(f"Database '{db_name}' not found.")
        return

    url = f"{BASE_URL}/databases/{db_id}"

    property_schema = generate_property_schema(prop_name, prop_type)

    data = {"properties": property_schema}

    if dry_run:
        print("DRY-RUN: would PATCH to:", url)
        print(json.dumps(data, indent=2))
        return

    try:
        resp = _request_with_retries("PATCH", url, headers=headers, json=data)
    except Exception as e:
        print("Error adding property:", e)
        return

    _save_last_response(resp)
    print("\n==== PROPERTY ADDED ====\n")
    try:
        print(resp.json())
    except Exception:
        print(resp.text)


    # ...existing code...
def get_database_schema(db_name):
    """Returns the property names of a database."""
    db_id = get_database_id(db_name)
    if not db_id:
        return {}

    url = f"{BASE_URL}/databases/{db_id}"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return {}

    data = response.json()
    return data.get("properties", {}).keys()

def add_relation_property(db_name, prop_name, target_db_name):
    """Adds a one-way relation property from db_name → target_db_name.
    Also checks for existing relations and prevents duplicates.
    """

    print(f"\n[RELATION] Preparing: {db_name}.{prop_name} → {target_db_name}")

    # Get source + target IDs
    source_id = get_database_id(db_name)
    target_id = get_database_id(target_db_name)

    if not source_id:
        print(f"[ERROR] Source database '{db_name}' not found.")
        return False

    if not target_id:
        print(f"[ERROR] Target database '{target_db_name}' not found.")
        return False

    # Check if property already exists
    existing = get_database_schema(db_name)
    if prop_name in existing:
        print(f"[SKIP] Relation '{prop_name}' already exists on '{db_name}'.")
        return True

    url = f"{BASE_URL}/databases/{source_id}"

    relation_schema = {
        prop_name: {
            "type": "relation",
            "relation": {"database_id": target_id}
        }
    }

    response = requests.patch(url, headers=headers, json={"properties": relation_schema})

    if response.status_code >= 200 and response.status_code < 300:
        print(f"[SUCCESS] Created one-way relation: {db_name}.{prop_name} → {target_db_name}")
        print("[NOTICE] Notion API cannot create reciprocal relations automatically.")
        return True
    else:
        print(f"[ERROR] Failed to create relation: {response.text}")
        return False

def generate_relation_checklist(relations):
    """Creates a Notion page listing all reciprocal relations to add manually."""

    checklist = "# Manual Reciprocal Relations Required\n\n"
    checklist += "Notion API limitation: Only one-way relations can be created via API.\n"
    checklist += "Add the following reciprocal properties manually in the Notion UI:\n\n"

    for source, prop, target in relations:
        checklist += f"- **{target} → {source}** (Reciprocal of '{source}.{prop}')\n"

    create_page("Missing Reciprocal Relations", checklist)
    print("\n[CHECKLIST CREATED] Added 'Missing Reciprocal Relations' page to Notion.")


def generate_property_schema(name, type):
    """Generates a Notion property schema based on type."""
    if type == "text":
        return {name: {"rich_text": {}}}

    if type == "select":
        return {name: {"select": {"options": []}}}

    if type == "multi-select":
        return {name: {"multi_select": {"options": []}}}

    if type == "number":
        return {name: {"number": {"format": "number"}}}

    if type == "date":
        return {name: {"date": {}}}

    if type == "url":
        return {name: {"url": {}}}

    if type == "relation":
        return {name: {"relation": [], "type": "relation"}}

    # Default fallback
    return {name: {"rich_text": {}}}


def create_page(title, content, dry_run=False):
    """Create a new page under NOTION_ROOT_PAGE with title and content."""
    url = f"{BASE_URL}/pages"

    # Break content into paragraph blocks to avoid Notion rich_text length limits.
    def _chunks_from_text(text, max_len=1900):
        # Split on double newlines first to preserve paragraphs
        paras = [p.strip() for p in text.split("\n\n") if p.strip()]
        chunks = []
        for p in paras:
            if len(p) <= max_len:
                chunks.append(p)
            else:
                # Fallback: wrap by words preserving readability
                import textwrap
                parts = textwrap.wrap(p, width=max_len, break_long_words=False, replace_whitespace=False)
                for part in parts:
                    if part.strip():
                        chunks.append(part)
        # If no paragraphs (single-line), ensure at least one chunk
        if not chunks and text.strip():
            chunks = [text.strip()]
        return chunks

    children = []
    for chunk in _chunks_from_text(content):
        children.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {"type": "text", "text": {"content": chunk}}
                ]
            }
        })

    data = {
        "parent": {"type": "page_id", "page_id": NOTION_ROOT_PAGE},
        "properties": {
            "title": [
                {"type": "text", "text": {"content": title}}
            ]
        },
        "children": children
    }

    if dry_run:
        print("DRY-RUN: would POST to:", url)
        print(json.dumps(data, indent=2))
        return

    if dry_run:
        print("DRY-RUN: would POST to:", url)
        print(json.dumps(data, indent=2))
        return None

    try:
        resp = _request_with_retries("POST", url, headers=headers, json=data)
    except Exception as exc:
        print("Error creating page:", exc)
        return None

    _save_last_response(resp)
    # Return response to caller for validation
    if 200 <= resp.status_code < 300:
        print("\n==== PAGE CREATED ====\n")
        try:
            print(resp.json())
        except Exception:
            print(resp.text)
        return resp
    else:
        print("\n==== NOTION ERROR ====\n")
        try:
            print(resp.json())
        except Exception:
            print(resp.text)
        return resp


def load_template(path):
    """Loads a template file from the templates/notion folder."""
    # Get project root by navigating up from this file
    project_root = Path(__file__).parent.parent.parent
    full_path = project_root / "templates" / "notion" / path
    
    if not full_path.exists():
        print(f"Template not found: {full_path}")
        return None
    
    with open(full_path, "r") as f:
        return f.read()


def create_template_page(template_path, title, variables=None):
    """Load a template, substitute variables, and create a Notion page."""
    if variables is None:
        variables = {}
    
    template = load_template(template_path)
    if not template:
        return
    
    # Replace variables in the template
    for key, value in variables.items():
        template = template.replace(f"{{{{{key}}}}}", value)
    
    # Send to Notion as a page
    create_page(title, template)


def generate_ai_filled_template(template_path, title, prompt):
    """Uses AI to fill template variables and generate a Notion page."""
    template = load_template(template_path)
    if not template:
        return

    print("\n=== Generating content with AI ===\n")
    print(f"Prompt: {prompt}\n")
    
    # Ask AI to produce the fields for the template
    ai_response = ask_ai(prompt)
    print(f"\nAI Response:\n{ai_response}\n")

    # Parse AI response as key: value pairs
    variables = {}
    for line in ai_response.split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip().lower()
            value = value.strip()
            variables[key] = value

    print(f"\nExtracted variables: {variables}\n")

    # Replace template variables with AI output
    filled_template = template
    for key, value in variables.items():
        filled_template = filled_template.replace(f"{{{{{key}}}}}", value)

    # Push filled template to Notion
    resp = create_page(title, filled_template)
    if resp and 200 <= getattr(resp, 'status_code', 0) < 300:
        print("\nAI-filled template generated successfully.")
    else:
        print("\nFailed to create AI-filled template in Notion.")


    if resp and 200 <= getattr(resp, 'status_code', 0) < 300:
        print("\nLesson generated successfully.")
    else:
        print("\nFailed to create lesson page in Notion.")

def generate_proposal(event_name):
    """Generates a full event proposal using AI templates."""
    # Resolve prompt file path from project root
    project_root = Path(__file__).parent.parent.parent
    prompt_path = project_root / "templates" / "notion" / "prompts" / "proposal_prompt.txt"
    try:
        with open(prompt_path, "r") as f:
            proposal_prompt = f.read()
    except FileNotFoundError:
        print("Proposal prompt file missing.")
        return

    # Ask AI to fill sections
    ai_response = ask_ai(proposal_prompt.replace("{{proposal_title}}", event_name))

    # Build variables dictionary
    variables = {}
    for line in ai_response.split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            variables[key.strip()] = value.strip()

    # Load proposal template
    template = load_template("proposals/event_proposal.txt")
    if not template:
        print("Proposal template missing.")
        return
    
    # Replace all placeholders
    for key, value in variables.items():
        template = template.replace(f"{{{{{key}}}}}", value)

    # Create page title
    page_title = f"Proposal: {event_name}"

    # Send to Notion
    resp = create_page(page_title, template)
    if resp and 200 <= getattr(resp, 'status_code', 0) < 300:
        print("\nProposal generated successfully.")
    else:
        print("\nFailed to create proposal page in Notion.")


def generate_speaker_profile(speaker_name):
    """Generates a full speaker or facilitator profile."""
    # Resolve prompt path from project root
    project_root = Path(__file__).parent.parent.parent
    prompt_path = project_root / "templates" / "notion" / "prompts" / "speaker_prompt.txt"
    try:
        with open(prompt_path, "r") as f:
            speaker_prompt = f.read()
    except FileNotFoundError:
        print("Speaker prompt file missing.")
        return

    # Ask AI to fill sections
    ai_response = ask_ai(speaker_prompt.replace("{{speaker_name}}", speaker_name))

    # Parse AI into dictionary
    variables = {}
    for line in ai_response.split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            variables[key.strip()] = value.strip()

    # Load template
    template = load_template("speakers/speaker_profile.txt")
    if not template:
        print("Speaker template missing.")
        return

    # Fill variables
    for key, value in variables.items():
        template = template.replace(f"{{{{{key}}}}}", value)

    # Create Notion page with Markdown folder link
    folder_path = create_speaker_folders(speaker_name)
    page_title = f"Speaker: {speaker_name}"
    content = template
    resp = create_page(page_title, content)
    page_id = None
    if resp and hasattr(resp, 'json'):
        try:
            page_id = resp.json().get('id')
        except Exception:
            pass
    if page_id:
        update_folder_path(page_id, folder_path)
        # Cloud sync
        import os
        cloud_path = os.path.join(CLOUD_ROOT, "Speakers", speaker_name)
        sync_folder(folder_path, cloud_path)
        update_page_property(page_id, "Cloud Folder", f"file://{cloud_path}")


def generate_tasks(project_title):

    # --- Minimal stubs for CLI routing ---
    # Remove nested function definitions that were incorrectly indented
    """Generates a task and timeline breakdown for a project."""
    from pathlib import Path
    # Load prompt using absolute path from project root
    project_root = Path(__file__).parent.parent.parent
    prompt_path = project_root / "templates" / "notion" / "prompts" / "task_prompt.txt"
    try:
        with open(prompt_path, "r") as f:
            task_prompt = f.read()
    except FileNotFoundError:
        print("Task prompt missing.")
        return

    # Ask AI for structured task fields
    ai_response = ask_ai(task_prompt.replace("{{project_title}}", project_title))

    # Parse into dictionary
    variables = {}
    for line in ai_response.split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            variables[key.strip()] = value.strip()

    # Load template
    template = load_template("events/task_list.txt")
    if not template:
        print("Task list template missing.")
        return

    # Fill placeholders
    for key, value in variables.items():
        template = template.replace(f"{{{{{key}}}}}", value)

    # Create Notion page
    page_title = f"Tasks: {project_title}"
    create_page(page_title, template)

    print("\nTask and timeline breakdown generated successfully.")

def generate_event_bundle(event_title):

    """Generates a full event package with multiple Notion pages."""

    # Create event folder and add folder path as property
    event_folder = create_event_folders(event_title)
    print(f"[EVENT FOLDER] Created at: {event_folder}")
    content = f"Event: {event_title}"
    resp = create_page(f"Event: {event_title}", content)
    event_page_id = None
    if resp and hasattr(resp, 'json'):
        try:
            event_page_id = resp.json().get('id')
        except Exception:
            pass
    if event_page_id:
        update_folder_path(event_page_id, event_folder)
        # Cloud sync
        import os
        cloud_path = os.path.join(CLOUD_ROOT, "Events", event_title)
        sync_folder(event_folder, cloud_path)
        update_page_property(event_page_id, "Cloud Folder", f"file://{cloud_path}")

    print(f"\nGenerating full event bundle for: {event_title}\n")

    # Generate event plan
    try:
        generate_event(event_title)
    except Exception as e:
        print(f"Error generating event plan: {e}")

    # Generate proposal
    try:
        generate_proposal(event_title)
    except Exception as e:
        print(f"Error generating proposal: {e}")

    # Generate task list
    try:
        generate_tasks(event_title)
    except Exception as e:
        print(f"Error generating tasks: {e}")

    # Generate onboarding
    try:
        generate_onboarding(event_title)
    except Exception as e:
        print(f"Error generating onboarding: {e}")

    print("\n*** Event Bundle Generated Successfully ***\n")

def install_ipe_machine():
    """Creates core Notion databases and standard properties for IPE + IndigiRise Accelerator."""

    print("\n=== Installing IPE Machine core structure ===\n")

    # 1. Core database names and their properties
    db_definitions = {
        "IPE Clients": [
            ("Status", "select"),
            ("Type", "select"),             # Nation, School, Corporate, Non-profit, Individual
            ("Primary Contact", "text"),
            ("Email", "text"),
            ("Phone", "text"),
            ("Programs", "multi-select")
        ],
        "IPE Events": [
            ("Client Name", "text"),
            ("Program", "select"),          # IndigiRise Accelerator, K-12, Life Skills, etc.
            ("Start Date", "date"),
            ("End Date", "date"),
            ("Status", "select"),           # Planning, Confirmed, In Delivery, Complete
            ("Location", "text"),
            ("Budget", "number")
        ],
        "IndigiRise Speakers & Facilitators": [
            ("Role", "text"),
            ("Type", "select"),             # Elder, Knowledge Keeper, Facilitator, Speaker
            ("Region", "text"),
            ("Fee Range", "text"),
            ("Email", "text"),
            ("Phone", "text")
        ],
        "K12 Indigenous Programs": [
            ("Grade Range", "text"),
            ("Delivery Model", "select"),   # In-person, Virtual, Hybrid
            ("Length", "text"),             # e.g., 1-day, 10-month package
            ("Status", "select"),
            ("Lead Facilitator", "text")
        ],
        "IPE Tasks": [
            ("Project / Event", "text"),
            ("Status", "select"),           # Not Started, In Progress, Complete
            ("Priority", "select"),         # High, Medium, Low
            ("Owner", "text"),
            ("Due Date", "date"),
            ("Category", "select")          # Admin, Curriculum, Logistics, Finance, Marketing
        ]
    }

    # 2. Create each database and add properties
    for db_name, properties in db_definitions.items():
        print(f"\nCreating database: {db_name}")
        resp = create_database(db_name)
        db_id = None
        if resp is not None:
            try:
                db_id = resp.json().get("id")
            except Exception:
                db_id = None
        if not db_id:
            print(f"  [WARN] Could not get database ID for {db_name}, skipping properties.")
            continue

def add_property_by_id(db_id, prop_name, prop_type, dry_run=False):
    url = f"{BASE_URL}/databases/{db_id}"
    property_schema = generate_property_schema(prop_name, prop_type)
    data = {"properties": property_schema}
    if dry_run:
        print("DRY-RUN: would PATCH to:", url)
        print(json.dumps(data, indent=2))
        return
    try:
        resp = _request_with_retries("PATCH", url, headers=headers, json=data)
    except Exception as e:
        print("Error adding property:", e)
        return
    _save_last_response(resp)
    print("\n==== PROPERTY ADDED ====")
    try:
        print(resp.json())
    except Exception:
        print(resp.text)
def _save_last_response(resp):
    _ensure_log_dir()
    try:
        body = resp.json()
    except Exception:
        body = {"text": resp.text}

    record = {
        "status_code": resp.status_code,
        "body": body,
        "headers": dict(resp.headers)
    }

    with open(LAST_RESPONSE_PATH, "w") as f:
        json.dump(record, f, indent=2)

def wire_ipe_relations():
    """Creates IPE Machine relations and generates manual reciprocal checklist."""

    print("\n=== Wiring IPE Machine Relations ===\n")

    relations = [
        ("IPE Events", "Client", "IPE Clients"),
        ("IPE Events", "Speakers / Facilitators", "IndigiRise Speakers & Facilitators"),
        ("IPE Tasks", "Event", "IPE Events"),
        ("IPE Clients", "Programs", "K12 Indigenous Programs"),
        ("K12 Indigenous Programs", "Lead Facilitator", "IndigiRise Speakers & Facilitators"),
        ("IPE Events", "Onboarding", "IPE Clients")
    ]

    for source, prop, target in relations:
        added = add_relation_property(source, prop, target)
        if added:
            print(f"[NEXT] Add reciprocal manually: {target} → {source}")

    # Build the Notion checklist page
    generate_relation_checklist(relations)

    print("\n=== Relation wiring complete ===\n")

    print("\n=== Wiring IPE Machine Relations ===\n")
    print("[INFO] Due to a Notion API limitation, only one-way relation properties can be created programmatically.\n"
          "To complete two-way (reciprocal) relations, you must manually add the reciprocal property in the Notion UI after this script runs.\n"
          "Each property created here will link to its target, but the reverse link must be set up manually in Notion.")

    try:
        add_relation_property("IPE Events", "Client", "IPE Clients")
        add_relation_property("IPE Events", "Speakers / Facilitators", "IndigiRise Speakers & Facilitators")
        add_relation_property("IPE Tasks", "Event", "IPE Events")
        add_relation_property("IPE Clients", "Programs", "K12 Indigenous Programs")
        add_relation_property("K12 Indigenous Programs", "Lead Facilitator", "IndigiRise Speakers & Facilitators")
        add_relation_property("IPE Events", "Onboarding", "IPE Clients")  # optional
    except Exception as e:
        print("Error wiring relations:", e)

    print("\n=== One-way relations created. To complete two-way links, add reciprocal relation properties in Notion UI. ===\n")
