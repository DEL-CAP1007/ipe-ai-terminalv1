from cli.commands.db_get import db_get_command
from cli.commands.db_find import db_find_command
from cli.commands.db_list import db_list_command
from cli.commands.query import query_command
from cli.commands.query_open import query_open_command
from cli.commands.sync_status import sync_status_command
from cli.commands.sync_trace import sync_trace_command
from cli.commands.sync_run import sync_run_command
from cli.commands.schema_validate import schema_validate_command
from cli.commands.schema_fix import schema_fix_command
from cli.commands.relations_get import relations_get_command
from cli.commands.relations_find import relations_find_command
from cli.commands.relations_graph import relations_graph_command
from cli.commands.relations_audit import relations_audit_command

COMMANDS = {
    "db.get": db_get_command,
    "db.find": db_find_command,
    "db.list": db_list_command,
    "query": query_command,
    "query.open": query_open_command,
    "sync.status": sync_status_command,
    "sync.trace": sync_trace_command,
    "sync.run": sync_run_command,
    "schema.validate": schema_validate_command,
    "schema.fix": schema_fix_command,
    "relations.get": relations_get_command,
    "relations.find": relations_find_command,
    "relations.graph": relations_graph_command,
    "relations.audit": relations_audit_command,
}

def route_command(cmd, args):
    if cmd in COMMANDS:
        return COMMANDS[cmd](args)
    return f"Unknown command: {cmd}"
