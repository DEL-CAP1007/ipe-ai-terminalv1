from services.entity_index import EntityIndexService
from cli.commands.query import format_results

def db_list_command(args):
    if not args:
        return "Usage: db.list <entity_type>"
    etype = args[0]
    entities = EntityIndexService.list_by_type(etype)
    return format_results(entities)
