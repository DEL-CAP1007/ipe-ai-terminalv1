import os, json, argparse, datetime, requests
from collections import Counter

NOTION_TOKEN = os.getenv("NOTION_TOKEN") or os.getenv("NOTION_API_KEY")
NOTION_VERSION = os.getenv("NOTION_VERSION", "2022-06-28")
NOTION_TASKS_DB_ID = os.getenv("NOTION_TASKS_DB_ID")

TITLE_PROP = "Name"
STATUS_PROP = "Status"
PRIORITY_PROP = "Priority"
CATEGORY_PROP = "Category"
NOTES_PROP = "Notes"

SUGGESTION_MARKER = "Suggested by Ops"
APPROVED_STAMP = "Approved by Ops"
REJECTED_STAMP = "Rejected by Ops"


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


def query_db(filter_obj: dict, limit: int):
    if not NOTION_TASKS_DB_ID:
        die("Missing NOTION_TASKS_DB_ID")
    body = {"page_size": min(limit, 100), "filter": filter_obj}
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


def plain_title(page):
    t = page.get("properties", {}).get(TITLE_PROP, {}).get("title", [])
    return "".join([x.get("plain_text", "") for x in t]).strip()


def plain_notes(page):
    rt = page.get("properties", {}).get(NOTES_PROP, {}).get("rich_text", [])
    return "".join([x.get("plain_text", "") for x in rt]).strip()


def select_name(page, prop):
    sel = page.get("properties", {}).get(prop, {}).get("select")
    return (sel or {}).get("name")


def build_item(page):
    return {
        "page_id": page.get("id"),
        "title": plain_title(page),
        "status": select_name(page, STATUS_PROP),
        "priority": select_name(page, PRIORITY_PROP),
        "category": select_name(page, CATEGORY_PROP),
        "url": page.get("url"),
        "notes": (plain_notes(page)[:220] if plain_notes(page) else ""),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=25, help="max items per section list")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--include-rejected", action="store_true")
    ap.add_argument("--include-approved", action="store_true")
    ap.add_argument("--days", type=int, default=None, help="optional lookback window (days) for approved/rejected sections")
    args = ap.parse_args()

    suggested_filter = {
        "and": [
            {"property": STATUS_PROP, "select": {"equals": "Waiting"}},
            {"property": NOTES_PROP, "rich_text": {"contains": SUGGESTION_MARKER}},
        ]
    }
    suggested_pages = query_db(suggested_filter, args.limit)
    suggested_items = [build_item(p) for p in suggested_pages]

    rejected_items = []
    if args.include_rejected:
        time_filter = []
        if args.days:
            ts = (datetime.datetime.utcnow() - datetime.timedelta(days=args.days)).isoformat()
            time_filter.append({"timestamp": "created_time", "created_time": {"on_or_after": ts}})
        rejected_filter = {
            "and": [
                {"property": STATUS_PROP, "select": {"equals": "Cancelled"}},
                {"property": NOTES_PROP, "rich_text": {"contains": REJECTED_STAMP}},
            ]
        }
        if time_filter:
            rejected_filter["and"].extend(time_filter)
        rejected_pages = query_db(rejected_filter, args.limit)
        rejected_items = [build_item(p) for p in rejected_pages]

    approved_items = []
    if args.include_approved:
        time_filter = []
        if args.days:
            ts = (datetime.datetime.utcnow() - datetime.timedelta(days=args.days)).isoformat()
            time_filter.append({"timestamp": "created_time", "created_time": {"on_or_after": ts}})
        approved_filter = {
            "and": [
                {"property": STATUS_PROP, "select": {"equals": "Not Started"}},
                {"property": NOTES_PROP, "rich_text": {"contains": APPROVED_STAMP}},
            ]
        }
        if time_filter:
            approved_filter["and"].extend(time_filter)
        approved_pages = query_db(approved_filter, args.limit)
        approved_items = [build_item(p) for p in approved_pages]

    cat_counts = Counter([it["category"] for it in suggested_items if it.get("category")])
    prio_counts = Counter([it["priority"] for it in suggested_items if it.get("priority")])

    payload = {
        "counts": {
            "suggested_queue": len(suggested_items),
            "rejected": len(rejected_items) if args.include_rejected else None,
            "approved": len(approved_items) if args.include_approved else None,
        },
        "top_categories_in_queue": cat_counts.most_common(10),
        "priority_counts_in_queue": {k: prio_counts.get(k, 0) for k in ["High", "Medium", "Low"]},
        "suggested_queue": suggested_items,
        "rejected": rejected_items if args.include_rejected else None,
        "approved": approved_items if args.include_approved else None,
    }

    if args.json:
        print(json.dumps(payload, ensure_ascii=False))
        return

    print("\n=== OPS QUEUE ===\n")
    window_txt = f"last {args.days}d" if args.days else "all time"
    print(f"Suggested queue (Waiting): {payload['counts']['suggested_queue']}")
    if args.include_rejected:
        print(f"Rejected (Cancelled + stamp, {window_txt}): {payload['counts']['rejected']}")
    if args.include_approved:
        print(f"Approved (Not Started + stamp, {window_txt}): {payload['counts']['approved']}")

    if payload["top_categories_in_queue"]:
        print("\nTop categories in queue:")
        for cat, n in payload["top_categories_in_queue"]:
            print(f"- {cat}: {n}")

    if any(payload["priority_counts_in_queue"].values()):
        print("\nPriority counts in queue:")
        for p in ["High", "Medium", "Low"]:
            print(f"- {p}: {payload['priority_counts_in_queue'][p]}")

    print("\nSuggested items:")
    if not suggested_items:
        print("(none)")
    else:
        for i, it in enumerate(suggested_items, 1):
            print(f"{i}. {it['title']}")
            print(f"   Status={it['status']} | Priority={it['priority']} | Category={it['category']}")
            print(f"   {it['url']}")
            print(f"   page_id={it['page_id']}")
            if it["notes"]:
                print(f"   notes: {it['notes']}")
            print()


if __name__ == "__main__":
    main()
