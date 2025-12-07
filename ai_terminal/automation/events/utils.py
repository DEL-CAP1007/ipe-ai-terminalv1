import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, Tuple

from notion.notion import post  # uses your existing Notion helpers

# Default root for Events on the T7 drive
DEFAULT_EVENTS_ROOT = "/Volumes/T7/IPE-Enterprise/Events"

def get_events_root() -> Path:
	"""
	Resolve the root folder where all event folders should be created.
	Allows override via IPE_EVENTS_ROOT env var, otherwise uses DEFAULT_EVENTS_ROOT.
	"""
	root = os.getenv("IPE_EVENTS_ROOT", DEFAULT_EVENTS_ROOT)
	return Path(root)

def sanitise_folder_name(name: str) -> str:
	"""
	Make a safe folder name from the event name.
	"""
	bad_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
	clean = name.strip()
	for ch in bad_chars:
		clean = clean.replace(ch, '-')
	# collapse double spaces
	while "  " in clean:
		clean = clean.replace("  ", " ")
	return clean

def build_event_folder_path(event_name: str, event_date: Optional[str] = None) -> Path:
	"""
	Build the full path for a new event.
	Example: /Volumes/T7/IPE-Enterprise/Events/2025-02-26 - Bringing the Children Home
	"""
	root = get_events_root()
	root.mkdir(parents=True, exist_ok=True)

	prefix = ""
	if event_date:
		try:
			# accept YYYY-MM-DD or other common formats
			dt = datetime.fromisoformat(event_date)
			prefix = dt.strftime("%Y-%m-%d") + " - "
		except Exception:
			# if parsing fails, just ignore the date in folder name
			prefix = ""

	folder_name = prefix + sanitise_folder_name(event_name)
	return root / folder_name

def create_event_folder_structure(base_path: Path) -> None:
	"""
	Create a standard folder structure inside the event folder.
	You can expand/customize this over time as your ops mature.
	"""
	subfolders = [
		"01 - Contracts & Proposals",
		"02 - Budget & Finance",
		"03 - Program & Run of Show",
		"04 - Speakers & Facilitators",
		"05 - Marketing & Media",
		"06 - Logistics & Vendors",
		"07 - Registration & Attendees",
		"08 - Reports & Debrief",
	]
	base_path.mkdir(parents=True, exist_ok=True)
	for folder in subfolders:
		(base_path / folder).mkdir(exist_ok=True)

def find_database_by_title(title: str) -> Optional[str]:
	"""
	Use Notion search to find a database by its title.
	Returns the database_id or None.
	"""
	payload = {
		"query": title,
		"filter": {"property": "object", "value": "database"},
	}
	resp = post("search", payload)
	results = resp.get("results", [])
	for obj in results:
		if obj.get("object") == "database":
			# Notion DB title is a list of rich_text
			db_title = ""
			title_prop = obj.get("title", [])
			if title_prop:
				db_title = title_prop[0].get("plain_text", "")
			if db_title.strip() == title.strip():
				return obj.get("id")
	return None

def build_event_properties(
	event_name: str,
	client_name: Optional[str],
	event_date: Optional[str],
	folder_path: Path,
	cloud_folder: Optional[str] = None,
) -> Dict[str, Any]:
	"""
	Build the properties payload for IPE Events (Master).
	Adjust property keys to match your Notion schema.
	"""
	props: Dict[str, Any] = {}

	# Event Name (title)
	props["Event Name"] = {
		"title": [
			{"type": "text", "text": {"content": event_name}}
		]
	}

	# Client (relation, placeholder for automation)
	props["Client"] = {"relation": []}

	# Event Type (select)
	props["Event Type"] = {"select": {"name": "Pitch Night"}}

	# Status (select)
	props["Status"] = {"select": {"name": "Planning"}}

	# Date of Event (date)
	if event_date:
		props["Date of Event"] = {"date": {"start": event_date}}
	else:
		props["Date of Event"] = {"date": {"start": None}}

	# Timeline Start (date)
	props["Timeline Start"] = {"date": {"start": None}}

	# Timeline End (date)
	props["Timeline End"] = {"date": {"start": None}}

	# Notes (rich_text)
	props["Notes"] = {"rich_text": [{"type": "text", "text": {"content": ""}}]}

	# Folder Path (url)
	props["Folder Path"] = {"url": str(folder_path)}

	# Cloud Folder (url)
	props["Cloud Folder"] = {"url": cloud_folder if cloud_folder else ""}

	# Relations (placeholders for automation)
	props["Tasks"] = {"relation": []}
	props["Clients"] = {"relation": []}
	props["Speakers & Facilitators"] = {"relation": []}
	props["Communication Log"] = {"relation": []}
	props["Programs"] = {"relation": []}
	props["Cohorts"] = {"relation": []}
	props["Participants"] = {"relation": []}

	return props

def parse_cli_event_date(raw: Optional[str]) -> Optional[str]:
	"""
	Normalise an input date string from CLI to ISO (YYYY-MM-DD) where possible.
	Returns None if no date or invalid.
	"""
	if not raw:
		return None
	raw = raw.strip()
	if not raw:
		return None
	try:
		# Accept common patterns; you can expand this over time if needed.
		dt = datetime.fromisoformat(raw)
		return dt.date().isoformat()
	except Exception:
		return None
