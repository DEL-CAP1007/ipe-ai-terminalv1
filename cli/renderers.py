def render_schema_validation_report(invalid):
    total = len(invalid)
    lines = [f"=== Schema Validation Report ===", f"Invalid entities: {total}"]
    for e, errors in invalid:
        lines.append(f"- {getattr(e, 'canonical_id', 'unknown')}")
        for err in errors:
            loc = '.'.join(str(x) for x in err.get('loc', []))
            msg = err.get('msg', '')
            lines.append(f"  - {loc}: {msg}")
    return "\n".join(lines)
from difflib import ndiff

def render_diff(old: dict, new: dict):
    lines = []
    keys = set(old.keys()) | set(new.keys())
    for k in keys:
        oldv = str(old.get(k, ""))
        newv = str(new.get(k, ""))
        if oldv != newv:
            lines.append(f"{k}:")
            diff = ndiff([oldv], [newv])
            lines.extend([f"  {line}" for line in diff])
    return "\n".join(lines)

def render_entity_card(entity):
    data = getattr(entity, 'data', {})
    tags = data.get("tags", [])
    lines = [
        f"=== {entity.canonical_id} ({entity.entity_type}) ===",
        f"Title: {data.get('title') or data.get('name')}",
        f"Status: {data.get('status')}  Priority: {data.get('priority')}",
        f"Tags: {', '.join(tags)}",
        f"Updated: {getattr(entity, 'last_modified', '')}",
        "",
        f"{data.get('description') or ''}",
    ]
    return "\n".join(lines)

def render_sync_status(status):
    lines = [
        "=== Sync Status ===",
        f"Last sync: {status.get('last_sync')}",
        f"Entities updated: {status.get('entities_updated')}",
        f"Conflicts resolved: {status.get('conflicts_resolved')}",
        f"Pending mappings: {status.get('pending_mappings')}",
        f"Drift detected: {status.get('drift_detected')}",
        f"Last error: {status.get('last_error')}",
        f"Active triggers: {status.get('active_triggers')}",
    ]
    return "\n".join(lines)

def render_sync_trace(trace):
    lines = [f"=== Sync Trace for {trace.get('canonical_id')} ==="]
    for event in trace.get('events', []):
        lines.append(f"{event['timestamp']}  {event['description']}")
    return "\n".join(lines)
