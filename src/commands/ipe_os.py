

from datetime import datetime
from typing import Optional
from commands.notion_helpers import get_page_by_title
from commands.notion import create_page

def upsert_page(title: str, parent_id: Optional[str] = None, content: str = "") -> str:
    """
    Checks if a page exists by title. If it does, returns its ID.
    Otherwise creates it under NOTION_ROOT_PAGE.
    NOTE: Your create_page() always uses NOTION_ROOT_PAGE as parent,
    so parent_id is kept for future expansion but not applied now.
    """
    from commands.notion import update_page_content
    existing = get_page_by_title(title)
    page_id = None
    if existing:
        print(f"[IPE OS] Using existing page: {title}")
        page_id = existing["id"]
    else:
        print(f"[IPE OS] Creating page: {title}")
        resp = create_page(title=title, content=content)
        if resp and isinstance(resp, dict):
            page_id = resp.get("id", None)
        elif hasattr(resp, "json"):
            try:
                json_data = resp.json()
                page_id = json_data.get("id")
            except Exception:
                return None
    if page_id:
        update_page_content(page_id, content)
        return page_id
    return None


def build_ipe_os():
    """
    Creates the full IPE OS structure:
    - Root OS page
    - 7 sub-dashboards
    - Pre-populated with headings and TODO view instructions
    """

    print("\n=== BUILDING IPE OS – ENTERPRISE COMMAND CENTER ===\n")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    # 1. ROOT PAGE
    root_content = f"""# IPE OS – Enterprise Command Center

Welcome to the operational brain of IPE Enterprise.

This system is the front-end for your VS Code + T7 AI Terminal automation.

Use the links below to navigate to operational dashboards:

- [[Home Dashboard]]
- [[Events Command Center]]
- [[K12 Programs Dashboard]]
- [[IndigiRise Accelerator Dashboard]]
- [[Speakers & Facilitators Dashboard]]
- [[IPE Tasks Master Timeline]]
- [[Automation & AI Terminal Guide]]
- [[IPE OS Documentation (System Map)]]

_Last built: {timestamp}_
"""
    root_page_id = upsert_page(
        "IPE OS – Enterprise Command Center",
        parent_id=None,
        content=root_content
    )

    # -------------------------------------------------------------
    # HOME DASHBOARD
    # -------------------------------------------------------------

    home_content = """# Home Dashboard

This is your CEO-level home view.

---

## 1. Today’s Tasks  
[TODO: Add a linked database view of **IPE Tasks**]

Suggested filter:
- Timeline Start = Today

---

## 2. This Week’s Tasks  
[TODO: Add a linked database view of **IPE Tasks**]

Filter:
- Timeline Start within next 7 days

---

## 3. Active Events  
[TODO: Add linked view of **IPE Events**]

Filter:
- Event Date is upcoming  
OR  
- Status = Active

---

## 4. Active K12 Programs  
[TODO: Linked view of **K12 Indigenous Programs**]

---

## 5. Active Accelerator Cohorts  
[TODO: Linked view of **IPE Events**]

Filter:
- Event Type = Accelerator Cohort  
OR Title contains “IndigiRise Accelerator”

---

## 6. Quick Automation Commands

Run from VS Code inside T7 project:

```bash
python src/main.py workflow full-event-schedule "Event Name" YYYY-MM-DD
python src/main.py workflow new-client "Client Name"
python src/main.py workflow timeline-k12 "Program Name" YYYY-MM-DD
python src/main.py workflow timeline-accelerator "Cohort Name" YYYY-MM-DD


"""
    upsert_page("Home Dashboard", parent_id=root_page_id, content=home_content)

    # -------------------------------------------------------------
    # EVENTS COMMAND CENTER
    # -------------------------------------------------------------

    events_content = """# Events Command Center


This is the control room for all IPE Events.

1. Events Overview

[TODO: Add a Table View of IPE Events]

Suggested Columns:

Name

Event Date

Client

Speakers

Folder Path

Cloud Folder

Status

2. Event Timeline

[TODO: Add Timeline View of IPE Tasks]

Filter:

Parent Event is not empty

Group by:

Parent Event

3. Countdown Tasks

[TODO: Add linked view of IPE Tasks]

Filter:

Name contains “T-”

4. Follow-Up Tasks

[TODO: Add linked view of IPE Tasks]

Filter:

Name contains “T+”
"""
    upsert_page("Events Command Center", parent_id=root_page_id, content=events_content)

    # -------------------------------------------------------------
    # K12 PROGRAMS DASHBOARD
    # -------------------------------------------------------------

    k12_content = """# K12 Programs Dashboard

Dashboard for K-12 Indigenous Education Programming.

1. K12 Program Overview

[TODO: Add Table View of K12 Indigenous Programs]

Columns:

Name

Client

Start Date

Folder Path

Cloud Folder

Status

2. Weekly Lesson Timeline

[TODO: Add Timeline View of IPE Tasks]

Filter:

Parent Program is not empty

3. K12 Deliverables

[TODO: Add linked view of IPE Tasks]

Filter:

Category = “K12 Deliverable”
"""
    upsert_page("K12 Programs Dashboard", parent_id=root_page_id, content=k12_content)

    # -------------------------------------------------------------
    # ACCELERATOR DASHBOARD
    # -------------------------------------------------------------

    accel_content = """# IndigiRise Accelerator Dashboard

Dashboard for Accelerator Cohorts and Pitch Nights.

1. Accelerator Cohorts

[TODO: Add Table or Gallery View of IPE Events]

Filter:

Event Type = Accelerator Cohort
OR Title contains “IndigiRise Accelerator”

2. 12-Week Accelerator Timeline

[TODO: Add Timeline View of IPE Tasks]

Filter:

Parent Event contains the cohort

Name contains “Week”

3. Pitch Night

[TODO: Add linked view of IPE Events]

Filter:

Title contains “Pitch Night”
"""
    upsert_page("IndigiRise Accelerator Dashboard", parent_id=root_page_id, content=accel_content)

    # -------------------------------------------------------------
    # SPEAKERS DASHBOARD
    # -------------------------------------------------------------

    speakers_content = """# Speakers & Facilitators Dashboard

This page supports the IPE Speakers & Facilitators Bureau.

1. Speaker Roster

[TODO: Add Table View of Speakers & Facilitators]

Suggested Columns:

Name

Nation

Offerings

Rate

Folder Path

2. Active Speaker Bookings

[TODO: Add linked view of IPE Tasks]

Filter:

Category = “Speaker Booking”
"""
    upsert_page("Speakers & Facilitators Dashboard", parent_id=root_page_id, content=speakers_content)

    # -------------------------------------------------------------
    # MASTER TASKS TIMELINE
    # -------------------------------------------------------------

    tasks_timeline_content = """# IPE Tasks Master Timeline

Full master timeline for all tasks across the enterprise.

[TODO: Add a Timeline View of IPE Tasks]

Suggested:

Group by Parent

Show ALL categories:

Event tasks

K12 timelines

Accelerator timelines

Countdown (T-)

Follow-ups (T+)

Daily ops

Weekly ops

Monthly ops
"""
    upsert_page("IPE Tasks Master Timeline", parent_id=root_page_id, content=tasks_timeline_content)

    # -------------------------------------------------------------
    # AUTOMATION GUIDE
    # -------------------------------------------------------------

    automation_content = """# Automation & AI Terminal Guide

How to use your VS Code AI Terminal + T7 to drive the IPE OS.

1. Terminal Project Location

Your automation project lives on the Samsung T7:

/Volumes/T7/IPE/

2. Key Workflow Commands
python src/main.py workflow full-event-schedule "Event" YYYY-MM-DD
python src/main.py workflow new-event "Event Name"
python src/main.py workflow new-client "Client Name"
python src/main.py workflow new-k12 "Program Name"
python src/main.py workflow timeline-event "Event Name" YYYY-MM-DD
python src.main.py workflow timeline-k12 "Program Name" YYYY-MM-DD
python src/main.py workflow timeline-accelerator "Cohort Name" YYYY-MM-DD

3. Folder System

Local Master (T7)

/Volumes/T7/IPE/
    Events/
    Clients/
    Speakers/
    K12/
    Onboarding/
    Templates/
    Archives/


Cloud Mirror (OneDrive)
Mirrors the same structure.

4. Notion Properties

Your OS relies on these:

Folder Path

Cloud Folder

Timeline Start

Timeline End

Parent relations
"""
    upsert_page("Automation & AI Terminal Guide", parent_id=root_page_id, content=automation_content)

    # -------------------------------------------------------------
    # SYSTEM MAP
    # -------------------------------------------------------------

    system_map_content = """# IPE OS Documentation (System Map)

This is your enterprise operating system architecture reference.

[TODO: Paste the full Phase 12 documentation here]

Recommended sections:

System Overview

Components

Databases

Folder Structure

Automation Layers

Workflow Engine

Schedule Engine

CLI Reference

Future Roadmap
"""
    upsert_page("IPE OS Documentation (System Map)", parent_id=root_page_id, content=system_map_content)

    print("\n=== IPE OS structure created/updated successfully ===\n")
    """
    Build the IPE OS structure in Notion:
    - Root: IPE OS – Enterprise Command Center
    - Subpages: Home, Events, K12, Accelerator, Speakers, Tasks, Automation Guide, System Map
    """

    print("\n=== Building IPE OS – Enterprise Command Center ===\n")

    # 1) Root page
    root_content = f"""# IPE OS – Enterprise Command Center

Welcome to the operational brain of IPE Enterprise.

This section is the *front-end* for your AI Terminal automation system.

Use the navigation links below to access each dashboard:

- [[Home Dashboard]]
- [[Events Command Center]]
- [[K12 Programs Dashboard]]
- [[IndigiRise Accelerator Dashboard]]
- [[Speakers & Facilitators Dashboard]]
- [[IPE Tasks Master Timeline]]
- [[Automation & AI Terminal Guide]]
- [[IPE OS Documentation (System Map)]]

_Last built: {datetime.now().strftime("%Y-%m-%d %H:%M")}_
"""
    root_page_id = upsert_page("IPE OS – Enterprise Command Center", parent_id=None, content=root_content)

    # 2) Home Dashboard
    home_content = """# Home Dashboard

This is your CEO-level home view.

---

## 1. Today’s Tasks

[TODO: Add a **linked database view** of IPE Tasks here]

Suggested filter:
- Timeline Start is **today**
- (Optional) Responsible contains “Natasha”

---

## 2. This Week’s Tasks

[TODO: Add a linked database view of IPE Tasks here]

Suggested filter:
- Timeline Start is within the **next 7 days**

---

## 3. Active Events

[TODO: Add a linked database view of IPE Events here]

Suggested filter ideas:
- Event Date is within the next 120 days **OR**
- Status = “Active”

---

## 4. Active K12 Programs

[TODO: Add a linked database view of K12 Indigenous Programs here]

Filter:
- Status = “Active”

---

## 5. Active Accelerator Cohorts

[TODO: Add a linked database view of IPE Events here]

Filter:
- Event Type = “Accelerator Cohort”
  OR
- Title contains “IndigiRise Accelerator”

---

## 6. Quick Commands (AI Terminal)

Use your VS Code terminal from the T7 project:

- Run full event schedule:

  ```bash
  python src/main.py workflow full-event-schedule "Bringing The Children Home" 2025-06-20
  ```

Run new client onboarding:

```bash
python src/main.py workflow new-client "Client Name"
```

Run K12 timeline:

```bash
python src/main.py workflow timeline-k12 "Program Name" 2025-09-01
```

You can add more examples here as you expand the system.
"""
    upsert_page("Home Dashboard", parent_id=root_page_id, content=home_content)

    events_content = """# Events OS Command Center

\n# Events OS Command Center\n\nOperational hub for all IPE events. Use the linked databases below to manage event planning, execution, communication, and reporting.\n\n---\n\n## 1. IPE Events (Master)\n\n➡️ **Add via:** /linked → IPE Events (Master)\n\nRecommended view: Table or Board\nSort by Event Date\nGroup by Event Status (if you have that property)\n\n---\n\n## 2. IPE Tasks (Master) — Events Only\n\n➡️ **Add via:** /linked → IPE Tasks (Master)\n\n**Filters:**\n- Parent Event → Is not empty\n- OR Category → Event Tasks\n\nThis gives you the entire event tasking system on one page.\n\n---\n\n## 3. IPE Clients (Master)\n\n➡️ **Add via:** /linked → IPE Clients (Master)\n\n**Filter:**\n- Events → Contains [Current Event] (if viewing a single event)\n- OR no filter (if viewing all event clients)\n\n---\n\n## 4. IndigiRise Speakers & Facilitators (Master)\n\n➡️ **Add via:** /linked → IndigiRise Speakers & Facilitators (Master)\n\n**Filter (optional):**\n- Events → Contains [Current Event]\n- OR none (for full directory)\n\n---\n\n## 5. Event Planning Templates\n\nAdd static text or checklists for:\n- Event Timeline Template\n- Run Sheet Template\n- Volunteer/Staffing Template\n- Marketing Timeline Template\n- Post-event Reporting Template\n\n(These are not databases — just static templates.)\n"""



    # 4) K12 Programs Dashboard
    k12_content = """# K12 Programs Dashboard


This dashboard is for K-12 Indigenous Education Packages.

1. Programs Overview


Suggested columns:

Name

Client

Folder Path

Cloud Folder
Status

2. Weekly Lesson Timeline

[TODO: Add a timeline view of IPE Tasks]

Parent Program (or equivalent relation) is not empty
These tasks are created by the K12 timeline builder in your AI Terminal.

3. Deliverables

[TODO: Add a linked view of IPE Tasks]

Filter idea:
"""

    # 5) IndigiRise Accelerator Dashboard
    accel_content = """# IndigiRise Accelerator Dashboard
[TODO: Add a table or gallery view of IPE Events]

Filter:

Event Type = "Accelerator Cohort"
OR

Title contains "IndigiRise Accelerator"

2. 12-Week Timeline

[TODO: Add a timeline view of IPE Tasks]

Filter:

Parent Event contains the cohort name

Task Name contains "Week"

These tasks are created by the accelerator timeline builder.

3. Pitch Night

[TODO: Add a linked view of IPE Events]

Filter:

Title contains "Pitch Night"
"""
    upsert_page("IndigiRise Accelerator Dashboard", parent_id=root_page_id, content=accel_content)

    # 6) Speakers & Facilitators Dashboard
    speakers_content = """# Speakers & Facilitators Dashboard

This dashboard supports the Speakers & Facilitators Bureau.

1. Speaker Roster

[TODO: Add a table view of the Speakers & Facilitators database]

Suggested columns:

Name

Nation

Offerings

Rate

Folder Path

2. Active Bookings

[TODO: Add a linked view of IPE Tasks]

Filter:

Category = "Speaker Booking"
"""
    upsert_page("Speakers & Facilitators Dashboard", parent_id=root_page_id, content=speakers_content)

    # 7) IPE Tasks Master Timeline
    tasks_timeline_content = """# IPE Tasks Master Timeline

This is the master timeline of all tasks in IPE.

[TODO: Add a timeline view of IPE Tasks here]

Suggested configuration:

View type: Timeline

Group by: Parent (Event / Program / Project)

Show all upcoming + recent tasks

This should show:

Event tasks

K12 lesson tasks

Accelerator tasks

Countdown tasks (T-)

Follow-up tasks (T+)

Daily / Weekly / Monthly operation cycles
"""
    upsert_page("IPE Tasks Master Timeline", parent_id=root_page_id, content=tasks_timeline_content)

    # 8) Automation & AI Terminal Guide
    automation_content = """# Automation & AI Terminal Guide

This page explains how to use the VS Code AI Terminal + T7 to drive the IPE OS.

1. Project Location

T7 root: /Volumes/T7/IPE/

Code project: e.g. /Volumes/T7/IPE/ipe-ai-terminal/ (adjust as needed)

2. Key Workflows (run from VS Code terminal)

Full event schedule:

python src/main.py workflow full-event-schedule "Event Name" YYYY-MM-DD


New event (bundle only):

python src/main.py workflow new-event "Event Name"


New client onboarding:

python src/main.py workflow new-client "Client Name"


New K12 program:

python src/main.py workflow new-k12 "Program Name"


Accelerator 12-week timeline:

python src/main.py workflow timeline-accelerator "Cohort Name" YYYY-MM-DD


Daily / weekly / monthly cycles:

python src/main.py workflow daily-cycle "IPE Operations" YYYY-MM-DD
python src/main.py workflow weekly-cycle "IPE Operations" YYYY-MM-DD
python src.main.py workflow monthly-cycle "IPE Operations" YYYY-MM-DD

3. Folder System

Local master (T7):

/Volumes/T7/IPE/
    Clients/
    Events/
    Speakers/
    K12/
    Onboarding/
    Templates/
    Archives/


Cloud mirror (OneDrive):

~/OneDrive - IPE Enterprise/IPE/
    Clients/
    Events/
    Speakers/
    K12/
    Onboarding/
    Templates/
    Archives/


Local is the source of truth. OneDrive is the cloud mirror.

4. Notion Integration

Each major DB has:

Folder Path (url to local T7 folder)

Cloud Folder (url to OneDrive folder)

Timeline Start / Timeline End (date fields)

The AI Terminal keeps these in sync.
"""
    upsert_page("Automation & AI Terminal Guide", parent_id=root_page_id, content=automation_content)

    # 9) IPE OS Documentation (System Map)
    system_map_content = """# IPE OS Documentation (System Map)

This is the high-level architecture reference for the IPE Machine.

[TODO: Paste the full System Map & Architecture Guide from Phase 12 here.]

Suggested sections:

System Overview

Core Components

Notion Databases

File System (T7 + OneDrive)

Automation Layers

Workflow Engine

Schedule Engine (Timelines & Cycles)

CLI Usage Reference

Future Roadmap
"""
    upsert_page("IPE OS Documentation (System Map)", parent_id=root_page_id, content=system_map_content)

    print("\n=== IPE OS structure created/updated successfully ===\n")
