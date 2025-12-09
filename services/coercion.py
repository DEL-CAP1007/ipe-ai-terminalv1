from dateutil import parser as date_parser

def coerce_entity_data(entity_type: str, data: dict) -> dict:
    d = dict(data)
    # normalize casing
    if "status" in d and isinstance(d["status"], str):
        d["status"] = d["status"].lower().strip()
    if "priority" in d and isinstance(d["priority"], str):
        d["priority"] = d["priority"].lower().strip()
    # tags as CSV
    if "tags" in d and isinstance(d["tags"], str):
        d["tags"] = [t.strip() for t in d["tags"].split(",") if t.strip()]
    # dates
    for field in ("created_at", "updated_at", "due_date"):
        if field in d and isinstance(d[field], str):
            try:
                d[field] = date_parser.parse(d[field])
            except Exception:
                pass
    return d
