from services.query_engine.semantic_service import SemanticQueryService
from cli.commands.query import format_results

def db_find_command(args):
    if not args:
        return "Usage: db.find \"<search text>\""
    text = " ".join(args).strip('"')
    results = SemanticQueryService.semantic_search_text(text)
    return format_results(results)
