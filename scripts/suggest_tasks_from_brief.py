import os, sys, json, argparse, subprocess, datetime
import requests
import hashlib
from pathlib import Path
from zoneinfo import ZoneInfo
from sqlalchemy import create_engine, text
from difflib import SequenceMatcher

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")

NOTION_TOKEN = os.getenv("NOTION_TOKEN") or os.getenv("NOTION_API_KEY")
NOTION_VERSION = os.getenv("NOTION_VERSION", "2022-06-28")
NOTION_TASKS_DB_ID = os.getenv("NOTION_TASKS_DB_ID")
OPS_BRIEF_TZ = os.getenv("OPS_BRIEF_TZ", "America/Edmonton")
DATABASE_URL = os.getenv("DATABASE_URL")

# Your Tasks DB schema (property names must match Notion exactly)
TASK_PROP_TITLE = "Name"
TASK_PROP_STATUS = "Status"
TASK_PROP_PRIORITY = "Priority"
TASK_PROP_CATEGORY = "Category"
TASK_PROP_NOTES = "Notes"
TASK_PROP_TIMELINE_START = "Timeline Start"
TASK_PROP_TIMELINE_END = "Timeline End"
TASK_PROP_CRITICAL = "Critical Task"
TASK_PROP_CLIENT = "Client"
TASK_PROP_PARENT_EVENT = "Parent Event"

STATUS_OPTIONS = {"Cancelled", "Not Started", "In Progress", "Completed", "Waiting", "Blocked"}
PRIORITY_OPTIONS = {"High", "Medium", "Low"}
CATEGORY_OPTIONS = {"Event", "K12", "Accelerator", "Speaker", "Admin", "Client", "Finance", "Deliverable", "Follow-up", "Countdown"}
SUGGESTION_MARKER = "Suggested by Ops"

def die(msg: str):
    raise SystemExit(f"[ERROR] {msg}")

def run_brief_json(preset: str, no_rollup: bool = False) -> dict:
    cmd = [
        sys.executable,
        os.path.join(ROOT, "scripts", "run_brief.py"),
        "--preset", preset,
        "--json",
    ]
    if no_rollup:
        cmd.append("--no-rollup")

    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(p.stderr.strip() or p.stdout.strip())
    return json.loads(p.stdout)

def notion_headers():
    if not NOTION_TOKEN:
        die("Missing NOTION_TOKEN/NOTION_API_KEY")
    return {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }

def openai_chat(prompt: str) -> str:
    if not OPENAI_API_KEY:
        die("Missing OPENAI_API_KEY")
    r = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"},
        json={
            "model": CHAT_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
        },
        timeout=120,
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"].strip()

def normalize_choice(val: str | None, allowed: set[str], default: str) -> str:
    if not val:
        return default
    v = str(val).strip()
    if v in allowed:
        return v
    v2 = v.title()
    if v2 in allowed:
        return v2
    return default

def iso_date(val: str | None) -> str | None:
    if not val:
        return None
    v = str(val).strip()
    if len(v) == 10 and v[4] == "-" and v[7] == "-":
        return v
    return None

def safe_bool(val) -> bool:
    if isinstance(val, bool):
        return val
    if isinstance(val, str):
        return val.strip().lower() in {"true", "yes", "1"}
    return False

def is_uuidish(s: str) -> bool:
    if not isinstance(s, str):
        return False
    s = s.strip()
    return len(s) >= 32 and all(c.isalnum() or c == "-" for c in s)


def norm(s: str) -> str:
    return " ".join("".join(ch.lower() if ch.isalnum() else " " for ch in s).split())


def score(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def fetch_candidates(engine, entity_type: str, limit: int = 50) -> list[dict]:
    sql = text(
        """
        SELECT title, canonical_id
        FROM entity
        WHERE entity_type = :t
        ORDER BY title
        LIMIT :lim
        """
    )
    with engine.begin() as conn:
        rows = conn.execute(sql, {"t": entity_type, "lim": limit}).fetchall()
    return [{"title": r[0], "canonical_id": r[1]} for r in rows]


def resolve_name_to_id(name: str, candidates: list[dict], min_score: float = 0.92) -> str | None:
    """
    Returns canonical_id if exactly one strong match is found.
    Strategy:
      1) exact normalized match
      2) best fuzzy match with uniqueness + threshold
    """
    n = norm(name)
    if not n:
        return None

    exact = [c for c in candidates if norm(c["title"]) == n]
    if len(exact) == 1:
        return exact[0]["canonical_id"]
    if len(exact) > 1:
        return None

    scored = []
    for c in candidates:
        s = score(n, norm(c["title"]))
        scored.append((s, c["canonical_id"], c["title"]))

    scored.sort(reverse=True, key=lambda x: x[0])
    if not scored:
        return None

    best = scored[0]
    if best[0] < min_score:
        return None

    if len(scored) > 1 and (best[0] - scored[1][0]) < 0.03:
        return None

    return best[1]


CACHE_DIR = Path(ROOT) / ".cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
LOCAL_LOG = CACHE_DIR / "task_suggestions.jsonl"


def make_suggestion_hash(t: dict) -> str:
    """
    Stable hash for dedupe. Ignores notes so the same intent is deduped even if wording changes.
    """
    key = {
        "name": (t.get("name") or "").strip().lower(),
        "status": t.get("status"),
        "priority": t.get("priority"),
        "category": t.get("category"),
        "critical": bool(t.get("critical_task")),
        "timeline_start": t.get("timeline_start") or "",
        "timeline_end": t.get("timeline_end") or "",
        "client_ids": sorted(t.get("client_ids") or []),
        "event_ids": sorted(t.get("parent_event_ids") or []),
    }
    blob = json.dumps(key, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def ensure_pg_dedupe_table(engine):
    sql = text(
        """
    CREATE TABLE IF NOT EXISTS task_suggestion (
      suggestion_hash text PRIMARY KEY,
      created_at timestamptz NOT NULL DEFAULT now(),
      preset text NOT NULL,
      task_name text NOT NULL,
      notion_page_id text
    );
    """
    )
    with engine.begin() as conn:
        conn.execute(sql)


def pg_seen_recent(engine, suggestion_hash: str, days: int) -> bool:
    sql = text(
        """
      SELECT 1
      FROM task_suggestion
      WHERE suggestion_hash = :h
        AND created_at >= now() - (:days || ' days')::interval
      LIMIT 1;
    """
    )
    with engine.begin() as conn:
        row = conn.execute(sql, {"h": suggestion_hash, "days": int(days)}).fetchone()
    return row is not None


def pg_log(engine, suggestion_hash: str, preset: str, task_name: str, page_id: str | None):
    sql = text(
        """
      INSERT INTO task_suggestion (suggestion_hash, preset, task_name, notion_page_id)
      VALUES (:h, :p, :n, :pid)
      ON CONFLICT (suggestion_hash)
      DO UPDATE SET notion_page_id = COALESCE(task_suggestion.notion_page_id, EXCLUDED.notion_page_id);
    """
    )
    with engine.begin() as conn:
        conn.execute(sql, {"h": suggestion_hash, "p": preset, "n": task_name, "pid": page_id})


def local_seen_recent(suggestion_hash: str, days: int) -> bool:
    if not LOCAL_LOG.exists():
        return False
    cutoff = datetime.datetime.utcnow() - datetime.timedelta(days=days)
    with LOCAL_LOG.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                obj = json.loads(line)
                if obj.get("suggestion_hash") != suggestion_hash:
                    continue
                ts = obj.get("created_at")
                if not ts:
                    continue
                dt = datetime.datetime.fromisoformat(ts.replace("Z", "+00:00"))
                if dt >= cutoff.replace(tzinfo=dt.tzinfo):
                    return True
            except Exception:
                continue
    return False


def local_log(suggestion_hash: str, preset: str, task_name: str, page_id: str | None):
    obj = {
        "suggestion_hash": suggestion_hash,
        "created_at": datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        "preset": preset,
        "task_name": task_name,
        "notion_page_id": page_id,
    }
    with LOCAL_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")

def build_prompt(brief: dict, max_tasks: int, known_clients: list[str] | None = None, known_events: list[str] | None = None) -> str:
    tz = ZoneInfo(OPS_BRIEF_TZ)
    now = datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M")
    sections = brief.get("sections", []) or []
    rollup = brief.get("rollup") or {}
    known_clients = known_clients or []
    known_events = known_events or []

    def compact_section(s: dict) -> str:
        label = s.get("preset", "section")
        q = s.get("query", label)
        hits = (s.get("hits") or [])[:8]
        lines = [f"### {label} — query: {q} — hits: {len(s.get('hits') or [])}"]
        for h in hits:
            lines.append(f"- [{h.get('entity_type','?')}] {h.get('title','')} (d={h.get('distance',0):.3f})")
        summ = s.get("summary") or {}
        if summ.get("summary_text"):
            lines.append(f"Summary: {summ['summary_text']}")
        return "\n".join(lines)

    body_parts = []
    body_parts.append(f"Time now: {now} ({OPS_BRIEF_TZ})")
    if rollup:
        body_parts.append("## Rollup")
        body_parts.append(json.dumps({
            "themes": rollup.get("themes", []),
            "next_actions": rollup.get("next_actions", []),
            "risks": rollup.get("risks", []),
            "summary_text": rollup.get("summary_text", "")
        }, ensure_ascii=False))
    body_parts.append("## Sections")
    for s in sections:
        body_parts.append(compact_section(s))

    allowed = {
        "status": sorted(STATUS_OPTIONS),
        "priority": sorted(PRIORITY_OPTIONS),
        "category": sorted(CATEGORY_OPTIONS),
    }

    allowed_relations_block = ""
    if known_clients or known_events:
        allowed_relations_block = (
            "\nRelation selection rules:\n"
            "- If you set client_names or event_names, you MUST choose exact strings from the Allowed Client Names / Allowed Event Names lists below.\n"
            "- If none apply confidently, omit client_names/event_names.\n\n"
            f"Allowed Client Names:\n{json.dumps(known_clients, ensure_ascii=False)}\n\n"
            f"Allowed Event Names:\n{json.dumps(known_events, ensure_ascii=False)}\n"
        )

    return f"""
You are an operations assistant for IPE Enterprise OS.

Using the brief below, propose up to {max_tasks} actionable tasks to create in the IPE Tasks (Master) database.

Hard rules:
- Output STRICT JSON only (no markdown, no commentary).
- Return an object with keys: tasks (array).
- Each task must have: name, status, priority, category, notes.
- Optional fields: timeline_start (YYYY-MM-DD), timeline_end (YYYY-MM-DD), critical_task (boolean).
- Optional relation fields by name (preferred): client_names (array of strings), event_names (array of strings).
- Optional relation fields by id: client_ids (array of Notion page IDs), parent_event_ids (array of Notion page IDs), ONLY if the ID is explicitly present in the brief. Do NOT invent IDs.
- If you are not confident about relations, omit them (do NOT guess IDs).
- If you set client_names or event_names, they must match exactly an item from the allowed lists (when provided).
- Keep names short, verb-led, specific. Notes must include a 1–2 sentence "why" tied to the brief.

Allowed values:
- status: {allowed["status"]}
- priority: {allowed["priority"]}
- category: {allowed["category"]}

{allowed_relations_block}

Brief:
{chr(10).join(body_parts)}
""".strip()

def validate_tasks(obj: dict, max_tasks: int) -> list[dict]:
    tasks = obj.get("tasks", [])
    if not isinstance(tasks, list):
        return []
    out = []
    for t in tasks[:max_tasks]:
        if not isinstance(t, dict):
            continue
        name = str(t.get("name", "")).strip()
        if not name:
            continue
        status = normalize_choice(t.get("status"), STATUS_OPTIONS, "Not Started")
        priority = normalize_choice(t.get("priority"), PRIORITY_OPTIONS, "Medium")
        category = normalize_choice(t.get("category"), CATEGORY_OPTIONS, "Admin")
        notes = str(t.get("notes", "")).strip() or "Auto-suggested from ops brief."
        ts = iso_date(t.get("timeline_start"))
        te = iso_date(t.get("timeline_end"))
        critical = safe_bool(t.get("critical_task"))
        client_ids = [x for x in (t.get("client_ids") or []) if is_uuidish(x)]
        event_ids = [x for x in (t.get("parent_event_ids") or []) if is_uuidish(x)]
        client_names = [str(x).strip() for x in (t.get("client_names") or []) if str(x).strip()]
        event_names = [str(x).strip() for x in (t.get("event_names") or []) if str(x).strip()]

        out.append({
            "name": name,
            "status": status,
            "priority": priority,
            "category": category,
            "notes": notes,
            "timeline_start": ts,
            "timeline_end": te,
            "critical_task": critical,
            "client_ids": client_ids,
            "parent_event_ids": event_ids,
            "client_names": client_names,
            "event_names": event_names,
        })
    return out

def notion_create_task(task: dict) -> str:
    if not NOTION_TASKS_DB_ID:
        die("Missing NOTION_TASKS_DB_ID")
    props = {
        TASK_PROP_TITLE: {"title": [{"type": "text", "text": {"content": task["name"]}}]},
        TASK_PROP_STATUS: {"select": {"name": task["status"]}},
        TASK_PROP_PRIORITY: {"select": {"name": task["priority"]}},
        TASK_PROP_CATEGORY: {"select": {"name": task["category"]}},
        TASK_PROP_NOTES: {"rich_text": [{"type": "text", "text": {"content": task["notes"]}}]},
        TASK_PROP_CRITICAL: {"checkbox": bool(task["critical_task"])}
    }
    if task.get("timeline_start"):
        props[TASK_PROP_TIMELINE_START] = {"date": {"start": task["timeline_start"]}}
    if task.get("timeline_end"):
        props[TASK_PROP_TIMELINE_END] = {"date": {"start": task["timeline_end"]}}
    if task.get("client_ids"):
        props[TASK_PROP_CLIENT] = {"relation": [{"id": cid} for cid in task["client_ids"]]}
    if task.get("parent_event_ids"):
        props[TASK_PROP_PARENT_EVENT] = {"relation": [{"id": eid} for eid in task["parent_event_ids"]]}

    body = {"parent": {"database_id": NOTION_TASKS_DB_ID}, "properties": props}
    r = requests.post("https://api.notion.com/v1/pages", headers=notion_headers(), json=body, timeout=60)
    r.raise_for_status()
    return r.json().get("id", "")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preset", default="ops.brief.daily", help="brief preset (default ops.brief.daily)")
    ap.add_argument("--max-tasks", type=int, default=7, help="max tasks to propose (default 7)")
    ap.add_argument("--apply", action="store_true", help="create tasks in Notion (default is dry-run)")
    ap.add_argument("--json", action="store_true", help="emit JSON only")
    ap.add_argument("--no-rollup", action="store_true", help="skip brief rollup generation")
    ap.add_argument("--dedupe-days", type=int, default=14, help="skip duplicates created within N days (default 14)")
    ap.add_argument("--no-dedupe", action="store_true", help="disable dedupe")
    ap.add_argument("--force", action="store_true", help="force create even if duplicate (overrides dedupe)")
    ap.add_argument("--review-mode", action="store_true", help="when --apply, create tasks as suggestions (Status=Waiting + marker)")
    ap.add_argument("--suggested-status", default="Waiting", help="status to use for suggestions (default Waiting)")
    args = ap.parse_args()

    brief = run_brief_json(args.preset, no_rollup=args.no_rollup)

    known_clients: list[str] = []
    known_events: list[str] = []
    engine = None
    client_candidates = []
    event_candidates = []

    if DATABASE_URL:
        engine = create_engine(DATABASE_URL)
        client_candidates = fetch_candidates(engine, "notion.client", limit=500)
        event_candidates = fetch_candidates(engine, "notion.event", limit=500)
        known_clients = [c.get("title") for c in client_candidates if c.get("title")][:50]
        known_events = [c.get("title") for c in event_candidates if c.get("title")][:50]

    debug = {
        "known_clients_count": len(known_clients),
        "known_events_count": len(known_events),
        "known_clients_sample": known_clients[:5],
        "known_events_sample": known_events[:5],
    }

    prompt = build_prompt(brief, max_tasks=args.max_tasks, known_clients=known_clients, known_events=known_events)
    raw = openai_chat(prompt)

    try:
        obj = json.loads(raw)
    except Exception:
        obj = {"tasks": []}

    tasks = validate_tasks(obj, max_tasks=args.max_tasks)

    dedupe_info = {
        "enabled": not args.no_dedupe,
        "force": bool(args.force),
        "days": args.dedupe_days,
        "backend": "pg" if engine else "local",
        "skipped": [],
        "errors": [],
    }

    result = {
        "preset": args.preset,
        "max_tasks": args.max_tasks,
        "apply": bool(args.apply),
        "models": {"chat": CHAT_MODEL},
        "debug": debug,
        "tasks": tasks,
        "created": [],
        "errors": [],
        "dedupe": dedupe_info,
    }

    # Auto-attach single known client/event names when clearly relevant and only one option exists
    def _mark_client_like(name: str, category: str) -> bool:
        txt = f"{name} {category}".lower()
        return any(k in txt for k in ["client", "follow", "proposal"])

    def _mark_event_like(name: str, category: str) -> bool:
        txt = f"{name} {category}".lower()
        return any(k in txt for k in ["event", "agenda", "speaker", "pitch", "logistic"])

    if len(known_clients) == 1 or len(known_events) == 1:
        only_client = known_clients[0] if len(known_clients) == 1 else None
        only_event = known_events[0] if len(known_events) == 1 else None
        for t in tasks:
            if only_client and not t.get("client_names") and _mark_client_like(t.get("name", ""), t.get("category", "")):
                t["client_names"] = [only_client]
            if only_event and not t.get("event_names") and _mark_event_like(t.get("name", ""), t.get("category", "")):
                t["event_names"] = [only_event]

    if DATABASE_URL:
        if engine is None:
            engine = create_engine(DATABASE_URL)
        if not client_candidates:
            client_candidates = fetch_candidates(engine, "notion.client", limit=500)
        if not event_candidates:
            event_candidates = fetch_candidates(engine, "notion.event", limit=500)

        for t in tasks:
            if not t.get("client_ids") and t.get("client_names"):
                resolved = []
                for nm in t["client_names"]:
                    cid = resolve_name_to_id(nm, client_candidates)
                    if cid:
                        resolved.append(cid)
                t["client_ids"] = list(dict.fromkeys(resolved))
                if not t["client_ids"] and t["client_names"]:
                    t["notes"] += " (Client match ambiguous or not found; relation skipped.)"

            if not t.get("parent_event_ids") and t.get("event_names"):
                resolved = []
                for nm in t["event_names"]:
                    eid = resolve_name_to_id(nm, event_candidates)
                    if eid:
                        resolved.append(eid)
                t["parent_event_ids"] = list(dict.fromkeys(resolved))
                if not t["parent_event_ids"] and t["event_names"]:
                    t["notes"] += " (Event match ambiguous or not found; relation skipped.)"

    # Precompute suggestion hashes for dedupe
    for t in tasks:
        t["suggestion_hash"] = make_suggestion_hash(t)

    if args.apply and args.review_mode:
        for t in tasks:
            t["status"] = args.suggested_status
            h = t.get("suggestion_hash", "")
            prefix = f"{SUGGESTION_MARKER} (hash={h})\n"
            if not t.get("notes", "").startswith(SUGGESTION_MARKER):
                t["notes"] = prefix + (t.get("notes", "") or "")

    dedupe_active = dedupe_info["enabled"] and not dedupe_info["force"]

    if dedupe_active and engine and args.apply:
        try:
            ensure_pg_dedupe_table(engine)
        except Exception as e:
            dedupe_info["errors"].append(f"pg_setup: {e}")
            # Fallback to local logging if PG not usable
            engine = None
            dedupe_info["backend"] = "local"

    if args.apply:
        for t in tasks:
            sh = t.get("suggestion_hash") or make_suggestion_hash(t)
            if dedupe_active:
                try:
                    seen = pg_seen_recent(engine, sh, args.dedupe_days) if engine else local_seen_recent(sh, args.dedupe_days)
                except Exception as e:
                    dedupe_info["errors"].append(f"dedupe_check: {t['name']}: {e}")
                    seen = False
                if seen:
                    dedupe_info["skipped"].append({"name": t["name"], "suggestion_hash": sh, "backend": dedupe_info["backend"]})
                    continue

            try:
                page_id = notion_create_task(t)
                result["created"].append({"name": t["name"], "page_id": page_id})
                try:
                    if engine:
                        pg_log(engine, sh, args.preset, t["name"], page_id)
                    else:
                        local_log(sh, args.preset, t["name"], page_id)
                except Exception as e:
                    dedupe_info["errors"].append(f"log: {t['name']}: {e}")
            except Exception as e:
                result["errors"].append({"name": t["name"], "error": str(e)})

    if args.json:
        print(json.dumps(result, ensure_ascii=False))
        return

    print("\n=== TASK SUGGESTIONS ===")
    print(f"Preset: {args.preset} | apply={args.apply} | max_tasks={args.max_tasks}\n")
    if not tasks:
        print("(no tasks suggested)")
        return
    for i, t in enumerate(tasks, start=1):
        print(f"{i}. {t['name']}")
        print(f"   Status: {t['status']} | Priority: {t['priority']} | Category: {t['category']} | Critical: {t['critical_task']}")
        if t.get("timeline_start") or t.get("timeline_end"):
            print(f"   Timeline: {t.get('timeline_start')} → {t.get('timeline_end')}")
        if t.get("client_ids"):
            print(f"   Client IDs: {', '.join(t['client_ids'])}")
        if t.get("parent_event_ids"):
            print(f"   Event IDs: {', '.join(t['parent_event_ids'])}")
        print(f"   Notes: {t['notes']}\n")

    if args.apply:
        print("=== CREATED IN NOTION ===")
        for c in result["created"]:
            print(f"- {c['name']} (page_id={c['page_id']})")
        if dedupe_info["skipped"]:
            print("\n=== SKIPPED (duplicates) ===")
            for s in dedupe_info["skipped"]:
                print(f"- {s['name']} (hash={s['suggestion_hash']} | backend={s['backend']})")
        if result["errors"]:
            print("\n=== ERRORS ===")
            for e in result["errors"]:
                print(f"- {e['name']}: {e['error']}")
        if dedupe_info["errors"]:
            print("\n=== DEDUPE WARNINGS ===")
            for msg in dedupe_info["errors"]:
                print(f"- {msg}")

    created_count = len(result.get("created", []))
    skipped_count = len(dedupe_info.get("skipped", []))
    error_count = len(result.get("errors", []))
    print(
        f"\nSummary → Created: {created_count} | "
        f"Skipped duplicates: {skipped_count} | "
        f"Errors: {error_count} | "
        f"Dedupe: {dedupe_info.get('backend', 'local')} ({dedupe_info.get('days', args.dedupe_days)}d)"
    )

if __name__ == "__main__":
    main()
