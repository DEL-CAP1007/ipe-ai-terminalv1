import os, sys, json, argparse, requests

NOTION_TOKEN = os.getenv("NOTION_TOKEN") or os.getenv("NOTION_API_KEY")
NOTION_VERSION = os.getenv("NOTION_VERSION", "2022-06-28")
NOTION_TASKS_DB_ID = os.getenv("NOTION_TASKS_DB_ID")

STATUS_PROP = "Status"
NOTES_PROP = "Notes"
TITLE_PROP = "Name"
SUGGESTION_MARKER = "Suggested by Ops"


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


def query_tasks(status: str, limit: int):
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
        "sorts": [{"property": "Timeline Start", "direction": "ascending"}],
    }

    out = []
    cursor = None
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


def get_title(page):
    props = page.get("properties", {})
    t = props.get(TITLE_PROP, {}).get("title", [])
    return "".join([x.get("plain_text", "") for x in t]).strip()


def get_notes(page):
    props = page.get("properties", {})
    rt = props.get(NOTES_PROP, {}).get("rich_text", [])
    return "".join([x.get("plain_text", "") for x in rt]).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--status", default="Waiting")
    ap.add_argument("--limit", type=int, default=25)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    pages = query_tasks(args.status, args.limit)

    items = []
    for p in pages:
        items.append({
            "page_id": p.get("id"),
            "title": get_title(p),
            "notes": get_notes(p)[:240],
            "url": p.get("url"),
        })

    if args.json:
        print(json.dumps({"count": len(items), "items": items}, ensure_ascii=False))
        return

    print(f"\n=== SUGGESTED TASKS QUEUE ({args.status}) ===\n")
    if not items:
        print("(none)")
        return
    for i, it in enumerate(items, 1):
        print(f"{i}. {it['title']}")
        print(f"   page_id={it['page_id']}")
        print(f"   {it['url']}")
        if it["notes"]:
            print(f"   notes: {it['notes']}")
        print()
if __name__ == "__main__":
    main()
