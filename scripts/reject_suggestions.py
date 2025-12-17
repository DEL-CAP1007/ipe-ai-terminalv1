import os, json, argparse, datetime, requests

NOTION_TOKEN = os.getenv("NOTION_TOKEN") or os.getenv("NOTION_API_KEY")
NOTION_VERSION = os.getenv("NOTION_VERSION", "2022-06-28")
NOTION_TASKS_DB_ID = os.getenv("NOTION_TASKS_DB_ID")

STATUS_PROP = "Status"
NOTES_PROP = "Notes"
TITLE_PROP = "Name"
SUGGESTION_MARKER = "Suggested by Ops"


def clean_page_ids(ids: list[str]) -> list[str]:
    out = []
    for x in ids:
        x = (x or "").strip()
        if not x or x == "--":
            continue
        if len(x) < 16:
            continue
        out.append(x)
    return out


def die(msg):
    raise SystemExit(f"[ERROR] {msg}")


def headers():
    if not NOTION_TOKEN:
        die("Missing NOTION_TOKEN/NOTION_API_KEY")
    return {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


def query_queue(status: str, limit: int):
    if not NOTION_TASKS_DB_ID:
        die("Missing NOTION_TASKS_DB_ID")
    body = {
        "page_size": min(limit, 100),
        "filter": {
            "and": [
                {"property": STATUS_PROP, "select": {"equals": status}},
                {"property": NOTES_PROP, "rich_text": {"contains": SUGGESTION_MARKER}},
            ]
        },
    }
    out, cursor = [], None
    while True:
        if cursor:
            body["start_cursor"] = cursor
        r = requests.post(
            f"https://api.notion.com/v1/databases/{NOTION_TASKS_DB_ID}/query",
            headers=headers(),
            json=body,
            timeout=60,
        )
        r.raise_for_status()
        data = r.json()
        out.extend(data.get("results", []))
        if len(out) >= limit:
            return out[:limit]
        if not data.get("has_more"):
            return out
        cursor = data.get("next_cursor")


def read_page(page_id: str):
    r = requests.get(f"https://api.notion.com/v1/pages/{page_id}", headers=headers(), timeout=60)
    r.raise_for_status()
    return r.json()


def extract_notes(page):
    rt = page.get("properties", {}).get(NOTES_PROP, {}).get("rich_text", [])
    return "".join([x.get("plain_text","") for x in rt]).strip()


def update_page(page_id: str, new_status: str, new_notes: str | None):
    props = {STATUS_PROP: {"select": {"name": new_status}}}
    if new_notes is not None:
        props[NOTES_PROP] = {"rich_text": [{"type": "text", "text": {"content": new_notes}}]}
    r = requests.patch(
        f"https://api.notion.com/v1/pages/{page_id}",
        headers=headers(),
        json={"properties": props},
        timeout=60,
    )
    r.raise_for_status()
    return r.json()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("page_ids", nargs="*", help="Notion page IDs to reject (omit when using --all)")
    ap.add_argument("--all", action="store_true", help="reject all suggested tasks in queue")
    ap.add_argument("--limit", type=int, default=25, help="max items when using --all")
    ap.add_argument("--queue-status", default="Waiting", help="queue status to pull from when using --all")
    ap.add_argument("--status", default="Cancelled", help="status to set on reject (default Cancelled)")
    ap.add_argument("--reason", default="", help="optional reason appended to Notes")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    ids = clean_page_ids(list(args.page_ids))
    if args.all:
        pages = query_queue(args.queue_status, args.limit)
        ids = clean_page_ids([p.get("id") for p in pages])

    if not ids:
        die("No page_ids provided and queue is empty (or limit=0).")

    results = {"rejected": [], "errors": []}
    stamp = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    reason_txt = f" Reason: {args.reason}" if args.reason else ""

    for pid in ids:
        try:
            page = read_page(pid)
            notes = extract_notes(page)
            rejection_line = f"Rejected by Ops ({stamp}).{reason_txt}"
            if rejection_line not in notes:
                new_notes = (notes + "\n\n" + rejection_line).strip() if notes else rejection_line
            else:
                new_notes = notes
            update_page(pid, args.status, new_notes)
            results["rejected"].append({"page_id": pid, "status": args.status})
        except Exception as e:
            results["errors"].append({"page_id": pid, "error": str(e)})

    if args.json:
        print(json.dumps(results, ensure_ascii=False))
        return

    print("\n=== REJECT RESULTS ===")
    for r in results["rejected"]:
        print(f"- rejected {r['page_id']} → {r['status']}")
    for e in results["errors"]:
        print(f"- ERROR {e['page_id']}: {e['error']}")


if __name__ == "__main__":
    main()
