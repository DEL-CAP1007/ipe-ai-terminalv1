from cli.renderers import render_entity_card
QUERY_CACHE = []

def format_results(results):
    global QUERY_CACHE
    QUERY_CACHE = results
    lines = []
    for i, r in enumerate(results, start=1):
        lines.append(f"[{i}] {r.canonical_id}  {r.title}")
        # ...other formatting...
    return "\n".join(lines)

def query_open_command(args):
    if not args:
        return "Usage: query open <index>"
    idx = int(args[0]) - 1
    if idx < 0 or idx >= len(QUERY_CACHE):
        return "Invalid index."
    entity = QUERY_CACHE[idx]
    return render_entity_card(entity)
