from services.query_engine.parser import parse_query_args
from services.query_engine.service import QueryService
from services.query_engine.semantic_service import SemanticQueryService
from db.session import get_session

def format_results(results):
    lines = []
    for i, r in enumerate(results, start=1):
        lines.append(f"[{i}] {r.canonical_id}  {r.title}")
        if r.status:
            lines.append(f"    status: {r.status}   priority: {r.priority or 'n/a'}")
        if r.tags:
            lines.append(f"    tags: {r.tags}")
        lines.append(f"    updated: {r.updated_at}")
        lines.append(f"    summary: {r.summary or ''}\n")
    return "\n".join(lines)

def query_command(args: list[str]):
    criteria = parse_query_args(args)
    with get_session() as db:
        if getattr(criteria, "semantic_text", None):
            results = SemanticQueryService.hybrid_search(db, criteria)
        else:
            results = QueryService.search(db, criteria)
    if not results:
        return "No results."
    return format_results(results)
