from services.query_engine.models import QueryCriteria

def parse_query_args(args: list[str]) -> QueryCriteria:
    """
    Parse the CLI args into a QueryCriteria object.
    """
    entity_type = None
    filters = {}
    tags = []
    search_text = None
    semantic_text = None
    limit = 50
    sort_field = None
    sort_dir = "desc"
    assignee = None
    owner = None

    # Identify first arg if it's entity_type
    if args and not args[0].startswith("--") and ":" not in args[0]:
        entity_type = args.pop(0).lower()
        if entity_type == "any":
            entity_type = None  # null means no entity filtering

    # Parse all remaining args
    i = 0
    while i < len(args):
        token = args[i]
        if token.startswith("tag:"):
            tags.append(token.split(":", 1)[1])
        elif ":" in token and not token.startswith("--"):
            field, value = token.split(":", 1)
            filters[field] = value
        elif token == "--search":
            i += 1
            search_text = args[i]
        elif token == "--semantic":
            i += 1
            semantic_text = args[i]
        elif token == "--limit":
            i += 1
            limit = int(args[i])
        elif token.startswith("--sort"):
            # format: --sort field:asc
            _, sort_info = token.split(" ", 1)
            sort_field, sort_dir = sort_info.split(":", 1)
        i += 1
    if "assignee" in filters:
        assignee = filters.pop("assignee")
    if "owner" in filters:
        owner = filters.pop("owner")
    return QueryCriteria(
        entity_type=entity_type,
        filters=filters,
        tags=tags,
        search_text=search_text,
        semantic_text=semantic_text,
        limit=limit,
        sort_field=sort_field,
        sort_dir=sort_dir,
        assignee=assignee,
        owner=owner,
    )
