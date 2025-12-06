import os
from typing import Optional

from notion.notion import post  # your existing HTTP wrapper
from ai_terminal.automation.events.utils import (
	build_event_folder_path,
	create_event_folder_structure,
	build_event_properties,
	parse_cli_event_date,
)
import os


def get_events_db_id() -> str:
	db_id = os.getenv("NOTION_ROOT_PAGE")
	if not db_id:
		raise EventCreationError("NOTION_ROOT_PAGE is not set in .env")
	return db_id


class EventCreationError(Exception):
	pass


def create_event(
	event_name: str,
	client_name: Optional[str] = None,
	event_date_raw: Optional[str] = None,
	cloud_folder: Optional[str] = None,
	dry_run: bool = False,
) -> str:
	"""
	Main function to create an Event in both:
	  1) Local filesystem (T7)
	  2) Notion IPE Events (Master) database

	Returns the created Notion page ID (or a description in dry_run mode).
	"""

	if not event_name or not event_name.strip():
		raise EventCreationError("Event name is required.")

	event_name = event_name.strip()
	event_date = parse_cli_event_date(event_date_raw)

	# 1) Resolve and create folder structure on T7
	folder_path = build_event_folder_path(event_name, event_date)
	if not dry_run:
		create_event_folder_structure(folder_path)

	# 2) Locate IPE Events (Master) database
	db_id = get_events_db_id()
	if not db_id:
		raise EventCreationError(
			f"Could not find Notion database titled '{EVENTS_DB_TITLE}'. "
			"Check the name and that the integration has access."
		)

	# 3) Build Notion properties
	props = build_event_properties(
		event_name=event_name,
		client_name=client_name,
		event_date=event_date,
		folder_path=folder_path,
		cloud_folder=cloud_folder,
	)

	payload = {
		"parent": {"type": "database_id", "database_id": db_id},
		"properties": props,
	}

	if dry_run:
		# Don't hit Notion, just return a summary string
		return (
			f"[DRY RUN] Would create event:\n"
			f"  Name: {event_name}\n"
			f"  Client: {client_name or '-'}\n"
			f"  Date: {event_date or '-'}\n"
			f"  Folder: {folder_path}\n"
			f"  DB: {db_id}"
		)

	resp = post("pages", payload)

	if resp.get("object") == "error":
		message = resp.get("message", "Unknown Notion error")
		raise EventCreationError(f"Failed to create event in Notion: {message}")

	page_id = resp.get("id")
	print("\n=== EVENT CREATED SUCCESSFULLY ===")
	print(f"Event:  {event_name}")
	print(f"Client: {client_name or '-'}")
	print(f"Date:   {event_date or '-'}")
	print(f"Folder: {folder_path}")
	print(f"Notion Page ID: {page_id}\n")

	return page_id


def cli_entry(event_name: str,
			  client_name: Optional[str] = None,
			  event_date: Optional[str] = None,
			  cloud_folder: Optional[str] = None,
			  dry_run: bool = False) -> None:
	"""
	Thin wrapper so your CLI can call this function.
	"""
	try:
		create_event(
			event_name=event_name,
			client_name=client_name,
			event_date_raw=event_date,
			cloud_folder=cloud_folder,
			dry_run=dry_run,
		)
	except EventCreationError as e:
		print(f"[EVENT ERROR] {e}")
	except Exception as e:
		print(f"[UNEXPECTED ERROR] {e}")
