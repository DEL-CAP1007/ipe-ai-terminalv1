import os
import shutil
import filecmp
# Local and Cloud root paths
LOCAL_ROOT = "/Volumes/T7/IPE"
CLOUD_ROOT = os.path.expanduser("~/OneDrive - IPE Enterprise/IPE")

def ensure_cloud_root():
    """Creates the cloud root folder in OneDrive if it does not exist."""
    if not os.path.exists(CLOUD_ROOT):
        os.makedirs(CLOUD_ROOT)
        print(f"[CLOUD ROOT CREATED] {CLOUD_ROOT}")
    else:
        print(f"[CLOUD ROOT EXISTS] {CLOUD_ROOT}")

def sync_folder(local_path, cloud_path):
    """One-way sync from Local (T7) → Cloud (OneDrive)."""
    # Create cloud path if missing
    ensure_folder(cloud_path)
    for root, dirs, files in os.walk(local_path):
        rel_path = os.path.relpath(root, local_path)
        target_root = os.path.join(cloud_path, rel_path)
        ensure_folder(target_root)
        # Sync files
        for file in files:
            local_file = os.path.join(root, file)
            cloud_file = os.path.join(target_root, file)
            # Only copy if missing or changed
            if not os.path.exists(cloud_file) or not filecmp.cmp(local_file, cloud_file):
                shutil.copy2(local_file, cloud_file)
                print(f"[SYNC] {local_file} → {cloud_file}")
            else:
                print(f"[SKIP] Already up-to-date: {cloud_file}")
def create_client_folders(client_name):
    """Creates folder structure for a new client."""
    path = os.path.join(ROOT_PATH, "Clients", client_name)
    subfolders = [
        "01 - Contracts & Agreements",
        "02 - Client Communication",
        "03 - Invoices & Payments",
        "04 - Event Files",
        "05 - K12 Programs",
        "06 - Notes"
    ]
    ensure_folder(path)
    for sub in subfolders:
        ensure_folder(os.path.join(path, sub))
    return path

def create_speaker_folders(speaker_name):
    """Creates folder structure for a speaker or facilitator."""
    path = os.path.join(ROOT_PATH, "Speakers", speaker_name)
    subfolders = [
        "01 - Bio & Photos",
        "02 - Agreements",
        "03 - Programs & Workshops",
        "04 - Event Bookings",
        "05 - Notes"
    ]
    ensure_folder(path)
    for sub in subfolders:
        ensure_folder(os.path.join(path, sub))
    return path

def create_k12_folders(program_name):
    """Creates folder structure for a K12 Indigenous Education Program."""
    path = os.path.join(ROOT_PATH, "K12", program_name)
    subfolders = [
        "01 - Curriculum",
        "02 - Activities",
        "03 - Materials",
        "04 - Facilitator Notes",
        "05 - Photos & Media",
        "06 - Reports"
    ]
    ensure_folder(path)
    for sub in subfolders:
        ensure_folder(os.path.join(path, sub))
    return path

def create_onboarding_folders(client_name):
    """Creates folder structure for onboarding a new client or program."""
    path = os.path.join(ROOT_PATH, "Onboarding", client_name)
    subfolders = [
        "01 - Discovery",
        "02 - Contracts",
        "03 - Project Setup",
        "04 - Meeting Notes",
        "05 - Assets",
        "06 - Reports"
    ]
    ensure_folder(path)
    for sub in subfolders:
        ensure_folder(os.path.join(path, sub))
    return path
import os

ROOT_PATH = "/Volumes/T7/IPE"

def ensure_folder(path):
    """Creates a folder if it does not already exist."""
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"[FOLDER CREATED] {path}")
    else:
        print(f"[EXISTS] {path}")

def install_master_folders():
    """Sets up the main IPE directory structure on the T7 SSD."""
    print("\n=== Creating IPE Master Folder Structure ===\n")
    main_folders = [
        "Clients",
        "Events",
        "Speakers",
        "Programs",
        "K12",
        "Onboarding",
        "Templates",
        "Archives"
    ]
    for folder in main_folders:
        ensure_folder(os.path.join(ROOT_PATH, folder))
    print("\n=== Master Folder Structure Complete ===\n")

def create_event_folders(event_name):
    """Creates the standardized folder structure for a new event."""
    path = os.path.join(ROOT_PATH, "Events", event_name)
    subfolders = [
        "01 - Admin",
        "02 - Proposals",
        "03 - Agenda",
        "04 - Speakers",
        "05 - Programming",
        "06 - Logistics",
        "07 - Budget",
        "08 - Marketing",
        "09 - Tasks",
        "10 - Notes"
    ]
    ensure_folder(path)
    for sub in subfolders:
        ensure_folder(os.path.join(path, sub))
    return path
