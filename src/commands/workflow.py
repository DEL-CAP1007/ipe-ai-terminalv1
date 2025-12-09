def workflow_full_event_schedule(event_name, event_date):
    print("\n=== FULL EVENT SCHEDULE WORKFLOW START ===\n")

    # 1. Generate full event bundle
    print("[1] Generating Event Bundle...")
    event_page_id = generate_event_bundle(event_name)

    # 2. Build countdown tasks (T-30, T-21, etc)
    print("[2] Building Countdown Tasks...")
    build_countdown(event_page_id, event_date)

    # 3. Build event timeline tasks
    print("[3] Building Event Timeline...")
    build_event_timeline(event_page_id, event_date)

    # 4. Build follow-up sequence (T+1, T+3, etc)
    print("[4] Building Follow-Up Tasks...")
    build_followups(event_page_id, event_date)

    # 5. Build DAILY operational cycle (30 days)
    print("[5] Building Daily Ops Cycle...")
    build_daily_ipe_cycle(event_page_id, event_date)

    # 6. Build WEEKLY operational cycle (12 weeks)
    print("[6] Building Weekly Ops Cycle...")
    build_weekly_ipe_cycle(event_page_id, event_date)

    # 7. Build MONTHLY operational cycle (6 months)
    print("[7] Building Monthly Ops Cycle...")
    build_monthly_ipe_cycle(event_page_id, event_date)

    # 8. Sync event folder T7 → OneDrive
    print("[8] Syncing Event Folder to Cloud...")
    local_path = f"{LOCAL_ROOT}/Events/{event_name}"
    cloud_path = f"{CLOUD_ROOT}/Events/{event_name}"
    sync_folder(local_path, cloud_path)

    print("\n=== FULL EVENT SCHEDULE WORKFLOW COMPLETE ===\n")

    return event_page_id
from commands.schedule import build_followups
def workflow_followup_event(event_name, event_date):
    page_id = get_event_page_id(event_name)
    build_followups(page_id, event_date)

from commands.notion import (
    generate_event_bundle,
    generate_onboarding,
    generate_k12,
    generate_speaker_profile,
    get_database_id
)
from commands.schedule import (
    build_event_timeline,
    build_k12_timeline,
    build_accelerator_timeline,
    build_daily_ipe_cycle,
    build_weekly_ipe_cycle,
    build_monthly_ipe_cycle,
    build_countdown
)
def workflow_countdown_event(event_name, event_date):
    event_page_id = get_event_page_id(event_name)
    build_countdown(event_page_id, event_date)
from commands.schedule import (
    build_event_timeline,
    build_k12_timeline,
    build_accelerator_timeline,
    build_daily_ipe_cycle,
    build_weekly_ipe_cycle,
    build_monthly_ipe_cycle
)
from commands.filesystem import sync_folder, LOCAL_ROOT, CLOUD_ROOT
import os

def workflow_new_event(event_name):
    print("[1] Generating Event Bundle...")
    generate_event_bundle(event_name)
    print("[2] Syncing Event Folder to OneDrive...")
    local_path = f"{LOCAL_ROOT}/Events/{event_name}"
    cloud_path = f"{CLOUD_ROOT}/Events/{event_name}"
    sync_folder(local_path, cloud_path)

def workflow_new_client(client_name):
    print("[1] Generating Client Onboarding...")
    generate_onboarding(client_name)
    print("[2] Syncing Client Folder to OneDrive...")
    local_path = f"{LOCAL_ROOT}/Clients/{client_name}"
    cloud_path = f"{CLOUD_ROOT}/Clients/{client_name}"
    sync_folder(local_path, cloud_path)

def workflow_new_k12(program_name):
    print("[1] Generating K12 Program...")
    generate_k12(program_name)
    print("[2] Syncing Program Folder to OneDrive...")
    local_path = f"{LOCAL_ROOT}/K12/{program_name}"
    cloud_path = f"{CLOUD_ROOT}/K12/{program_name}"
    sync_folder(local_path, cloud_path)

def workflow_new_pitchnight(event_name):
    print("[1] Generating IndigiRise Accelerator Pitch Night Bundle...")
    generate_event_bundle(event_name)
    print("[2] Syncing Accelerator Folder to OneDrive...")
    local_path = f"{LOCAL_ROOT}/Events/{event_name}"
    cloud_path = f"{CLOUD_ROOT}/Events/{event_name}"
    sync_folder(local_path, cloud_path)


# Timeline workflow integrations
def get_event_page_id(event_name):
    # Placeholder: implement actual lookup logic
    # For now, just return event_name (should be Notion page ID)
    return event_name

def get_project_or_page_id(name):
    # Placeholder: use event page lookup for now
    return get_event_page_id(name)
def workflow_daily_cycle(parent_name, start_date):
    parent_id = get_project_or_page_id(parent_name)
    build_daily_ipe_cycle(parent_id, start_date)

def workflow_weekly_cycle(parent_name, start_date):
    parent_id = get_project_or_page_id(parent_name)
    build_weekly_ipe_cycle(parent_id, start_date)

def workflow_monthly_cycle(parent_name, start_date):
    parent_id = get_project_or_page_id(parent_name)
    build_monthly_ipe_cycle(parent_id, start_date)
def get_k12_page_id(program_name):
    # Placeholder: implement actual lookup logic
    return program_name

def workflow_timeline_event(target_name, event_date):
    page_id = get_event_page_id(target_name)
    build_event_timeline(page_id, event_date)

def workflow_timeline_k12(target_name, start_date):
    page_id = get_k12_page_id(target_name)
    build_k12_timeline(page_id, start_date)

def workflow_timeline_accelerator(target_name, start_date):
    page_id = get_event_page_id(target_name)
    build_accelerator_timeline(page_id, start_date)

def run_workflow(workflow_name, *args):
    print(f"\n=== Running Workflow: {workflow_name} | Args: {args} ===\n")
    workflows = {
        "new-event": workflow_new_event,
        "new-client": workflow_new_client,
        "new-k12": workflow_new_k12,
        "new-pitchnight": workflow_new_pitchnight,
        "timeline-event": workflow_timeline_event,
        "timeline-k12": workflow_timeline_k12,
        "timeline-accelerator": workflow_timeline_accelerator,
        "daily-cycle": workflow_daily_cycle,
        "weekly-cycle": workflow_weekly_cycle,
        "monthly-cycle": workflow_monthly_cycle,
        "countdown-event": workflow_countdown_event,
        "followup-event": workflow_followup_event,
        "full-event-schedule": workflow_full_event_schedule
    }
        from db.session import get_session
        from services.audit.service import AuditService
        with get_session() as db:
            AuditService.log(
                db,
                identity=None,  # Pass actual identity if available
                action="pipeline.run",
                target_type="pipeline",
                target_id=workflow_name,
                target_label=workflow_name,
                metadata={"args": args},
                status="success",
            )
    if workflow_name not in workflows:
        print(f"[ERROR] Unknown workflow: {workflow_name}")
        print(f"Available workflows: {list(workflows.keys())}")
        return
    workflows[workflow_name](*args)
    print(f"\n=== Workflow Complete: {workflow_name} | Args: {args} ===\n")
