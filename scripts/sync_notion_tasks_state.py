import os, sys, json, time, argparse, hashlib, datetime
import requests
from sqlalchemy import create_engine, text

ENTITY_TYPE_TASK = "notion.task"
ENTITY_TYPE_CLIENT = "notion.client"
ENTITY_TYPE_EVENT = "notion.event"

REL_TASK_CLIENT = "task->client"
REL_TASK_EVENT = "task->event"

NOTION_TOKEN = os.getenv("NOTION_TOKEN") or os.getenv("NOTION_API_KEY")
NOTION_VERSION = os.getenv("NOTION_VERSION", "2022-06-28")
NOTION_TASKS_DB_ID = os.getenv("NOTION_TASKS_DB_ID")

DATABASE_URL = os.getenv("DATABASE_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_EMBED_MODEL = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")

# Tasks DB property names (match your schema)
PROP_TITLE = "Name"
PROP_STATUS = "Status"
PROP_PRIORITY = "Priority"
PROP_CATEGORY = "Category"
PROP_NOTES = "Notes"
PROP_ASSIGNED = "Assigned to"
PROP_TL_START = "Timeline Start"
PROP_TL_END = "Timeline End"
PROP_CRITICAL = "Critical Task"
PROP_CLIENT = "Client"
PROP_PARENT_EVENT = "Parent Event"


def die(msg: str):
    raise SystemExit(f"[ERROR] {msg}")


def notion_headers():
    if not NOTION_TOKEN:
        die("Missing NOTION_TOKEN/NOTION_API_KEY")
    return {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


def sha256_json(obj) -> str:
    blob = json.dumps(obj, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def extract_title(page) -> str:
    t = page.get("properties", {}).get(PROP_TITLE, {}).get("title", [])
    s = "".join([x.get("plain_text", "") for x in t]).strip()
    return s or "(Untitled Task)"


def extract_rich_text(page, prop) -> str:
    rt = page.get("properties", {}).get(prop, {}).get("rich_text", [])
    return "".join([x.get("plain_text", "") for x in rt]).strip()


def extract_select(page, prop) -> str | None:
    sel = page.get("properties", {}).get(prop, {}).get("select")
    return (sel or {}).get("name")


def extract_date(page, prop) -> dict | None:
    d = page.get("properties", {}).get(prop, {}).get("date")
    return d or None


def extract_checkbox(page, prop) -> bool:
    v = page.get("properties", {}).get(prop, {}).get("checkbox")
    return bool(v)


def extract_people(page, prop) -> list[dict]:
    ppl = page.get("properties", {}).get(prop, {}).get("people", []) or []
    out = []
    for p in ppl:
        out.append({
            "id": p.get("id"),
            "name": p.get("name"),
            "email": (p.get("person") or {}).get("email"),
        })
    return out


def extract_relation_ids(page, prop) -> list[str]:
    rel = page.get("properties", {}).get(prop, {}).get("relation", []) or []
    return [r.get("id") for r in rel if r.get("id")]


def openai_embed(text_in: str) -> list[float]:
    if not OPENAI_API_KEY:
        die("Missing OPENAI_API_KEY (needed for embeddings)")
    r = requests.post(
        "https://api.openai.com/v1/embeddings",
        headers={"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"},
        json={"model": OPENAI_EMBED_MODEL, "input": text_in},
        timeout=120,
    )
    r.raise_for_status()
    return r.json()["data"][0]["embedding"]


def notion_query_pages(limit: int, updated_since: str | None = None):
    if not NOTION_TASKS_DB_ID:
        die("Missing NOTION_TASKS_DB_ID")

    url = f"https://api.notion.com/v1/databases/{NOTION_TASKS_DB_ID}/query"
    out = []
    cursor = None

    while True:
        body = {"page_size": min(100, max(1, limit - len(out)))}

        if updated_since:
            body["filter"] = {"timestamp": "last_edited_time", "last_edited_time": {"on_or_after": updated_since}}

        if cursor:
            body["start_cursor"] = cursor

        r = requests.post(url, headers=notion_headers(), json=body, timeout=60)
        r.raise_for_status()
        data = r.json()
        out.extend(data.get("results", []))

        if len(out) >= limit:
            return out[:limit]
        if not data.get("has_more"):
            return out
        cursor = data.get("next_cursor")


def ensure_tables(engine):
    with engine.begin() as conn:
        conn.execute(text(
            """
        CREATE TABLE IF NOT EXISTS notion_sync_checkpoint (
          key text PRIMARY KEY,
          value text NOT NULL,
          updated_at timestamptz NOT NULL DEFAULT now()
        );
        """
        ))


def get_checkpoint(engine, key: str) -> str | None:
    with engine.begin() as conn:
        row = conn.execute(text("SELECT value FROM notion_sync_checkpoint WHERE key=:k"), {"k": key}).fetchone()
    return row[0] if row else None


def set_checkpoint(engine, key: str, value: str):
    with engine.begin() as conn:
        conn.execute(text(
            """
          INSERT INTO notion_sync_checkpoint(key, value) VALUES(:k, :v)
          ON CONFLICT (key) DO UPDATE SET value=EXCLUDED.value, updated_at=now()
        """
        ), {"k": key, "v": value})


def get_or_create_entity_id(conn, entity_type: str, canonical_id: str, title: str):
    row = conn.execute(text(
        """
        SELECT id FROM entity WHERE entity_type=:t AND canonical_id=:c
        LIMIT 1
    """
    ), {"t": entity_type, "c": canonical_id}).fetchone()
    if row:
        return row[0]

    row = conn.execute(text(
        """
        INSERT INTO entity(entity_type, canonical_id, title, metadata_json)
        VALUES (:t, :c, :title, '{}'::jsonb)
        RETURNING id
    """
    ), {"t": entity_type, "c": canonical_id, "title": title}).fetchone()
    return row[0]


def upsert_entity_task(conn, canonical_id: str, title: str, metadata: dict, content_blob: dict):
    new_hash = sha256_json(content_blob)

    row = conn.execute(text(
        """
        SELECT id,
               COALESCE(metadata_json, '{}'::jsonb) AS metadata_json,
               (metadata_json->>'content_hash') AS prev_hash
        FROM entity
        WHERE entity_type=:t AND canonical_id=:c
        LIMIT 1
    """
    ), {"t": ENTITY_TYPE_TASK, "c": canonical_id}).fetchone()

    if not row:
        merged = dict(metadata)
        merged["content_hash"] = new_hash
        ent = conn.execute(text(
            """
            INSERT INTO entity(entity_type, canonical_id, title, metadata_json)
            VALUES (:t, :c, :title, :m::jsonb)
            RETURNING id
        """
        ), {"t": ENTITY_TYPE_TASK, "c": canonical_id, "title": title, "m": json.dumps(merged)}).fetchone()
        return ent[0], None, new_hash

    entity_id = row[0]
    prev_hash = row[2]

    merged = metadata.copy()
    merged["content_hash"] = new_hash

    conn.execute(text(
        """
        UPDATE entity
        SET title = :title,
            metadata_json = COALESCE(metadata_json, '{}'::jsonb) || :m::jsonb
        WHERE id = :id
    """
    ), {"title": title, "m": json.dumps(merged), "id": entity_id})

    return entity_id, prev_hash, new_hash


def upsert_embedding(conn, entity_id: int, vector: list[float]):
    conn.execute(text(
        """
      INSERT INTO entity_embedding(entity_id, embedding, model)
      VALUES (:eid, :emb::vector, :model)
      ON CONFLICT (entity_id)
      DO UPDATE SET embedding = EXCLUDED.embedding, model = EXCLUDED.model
    """
    ), {"eid": entity_id, "emb": str(vector), "model": OPENAI_EMBED_MODEL})


def ensure_relation(conn, source_id: int, target_id: int, rel_type: str):
    exists = conn.execute(text(
        """
      SELECT 1 FROM entity_relation
      WHERE source_entity_id=:s AND target_entity_id=:t AND relation_type=:r
      LIMIT 1
    """
    ), {"s": source_id, "t": target_id, "r": rel_type}).fetchone()
    if exists:
        return
    conn.execute(text(
        """
      INSERT INTO entity_relation(source_entity_id, target_entity_id, relation_type, metadata_json)
      VALUES (:s, :t, :r, '{}'::jsonb)
    """
    ), {"s": source_id, "t": target_id, "r": rel_type})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=500, help="max tasks to scan (default 500)")
    ap.add_argument("--since", default=None, help="ISO datetime for Notion last_edited_time filter (optional)")
    ap.add_argument("--use-checkpoint", action="store_true", help="use DB checkpoint for incremental sync")
    ap.add_argument("--no-embed", action="store_true", help="skip embedding updates")
    ap.add_argument("--no-relations", action="store_true", help="skip entity_relation updates")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if not DATABASE_URL:
        die("Missing DATABASE_URL (needed for Phase 19.1 sync)")
    engine = create_engine(DATABASE_URL)
    ensure_tables(engine)

    since = args.since
    if args.use_checkpoint and not since:
        since = get_checkpoint(engine, "tasks_last_edited_since")

    pages = notion_query_pages(args.limit, updated_since=since)

    processed = 0
    embedded = 0
    skipped_embed = 0
    rel_links = 0
    max_last_edited = None

    with engine.begin() as conn:
        for page in pages:
            canonical_id = page["id"]
            title = extract_title(page)

            last_edited = page.get("last_edited_time")
            if last_edited:
                if (max_last_edited is None) or (last_edited > max_last_edited):
                    max_last_edited = last_edited

            status = extract_select(page, PROP_STATUS)
            priority = extract_select(page, PROP_PRIORITY)
            category = extract_select(page, PROP_CATEGORY)
            notes = extract_rich_text(page, PROP_NOTES)
            assigned = extract_people(page, PROP_ASSIGNED)
            tl_start = extract_date(page, PROP_TL_START)
            tl_end = extract_date(page, PROP_TL_END)
            critical = extract_checkbox(page, PROP_CRITICAL)

            client_ids = extract_relation_ids(page, PROP_CLIENT)
            event_ids = extract_relation_ids(page, PROP_PARENT_EVENT)

            metadata = {
                "status": status,
                "priority": priority,
                "category": category,
                "assigned_to": assigned,
                "timeline_start": tl_start,
                "timeline_end": tl_end,
                "critical_task": critical,
                "client_ids": client_ids,
                "parent_event_ids": event_ids,
                "notion_url": page.get("url"),
                "last_edited_time": last_edited,
            }

            content_blob = {
                "title": title,
                "status": status,
                "priority": priority,
                "category": category,
                "assigned_to": assigned,
                "timeline_start": tl_start,
                "timeline_end": tl_end,
                "critical_task": critical,
                "notes": notes,
                "client_ids": client_ids,
                "parent_event_ids": event_ids,
            }

            entity_id, prev_hash, new_hash = upsert_entity_task(conn, canonical_id, title, metadata, content_blob)
            processed += 1

            if not args.no_relations:
                for cid in client_ids:
                    tgt_id = get_or_create_entity_id(conn, ENTITY_TYPE_CLIENT, cid, "(Untitled Client)")
                    ensure_relation(conn, entity_id, tgt_id, REL_TASK_CLIENT)
                    rel_links += 1
                for eid in event_ids:
                    tgt_id = get_or_create_entity_id(conn, ENTITY_TYPE_EVENT, eid, "(Untitled Event)")
                    ensure_relation(conn, entity_id, tgt_id, REL_TASK_EVENT)
                    rel_links += 1

            if not args.no_embed:
                if prev_hash == new_hash:
                    skipped_embed += 1
                else:
                    text_for_embed = json.dumps(content_blob, ensure_ascii=False)
                    vec = openai_embed(text_for_embed)
                    upsert_embedding(conn, entity_id, vec)
                    embedded += 1

    if args.use_checkpoint and max_last_edited:
        with engine.begin() as conn:
            set_checkpoint(engine, "tasks_last_edited_since", max_last_edited)

    result = {
        "limit": args.limit,
        "since": since,
        "use_checkpoint": args.use_checkpoint,
        "max_last_edited_seen": max_last_edited,
        "processed": processed,
        "embedded": embedded,
        "skipped_embed": skipped_embed,
        "relation_links_written": rel_links,
        "no_embed": args.no_embed,
        "no_relations": args.no_relations,
    }

    if args.json:
        print(json.dumps(result, ensure_ascii=False))
        return

    print("\n=== TASK STATE SYNC ===")
    for k, v in result.items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    main()