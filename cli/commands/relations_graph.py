from services.relationship_service import RelationshipService
from cli.renderers import render_relation_graph
from db.session import get_session

def relations_graph_command(args):
    if not args:
        return "Usage: relations.graph <canonical_id>"
    canonical_id = args[0]
    depth = int(args[1]) if len(args) > 1 else 2
    with get_session() as db:
        graph = RelationshipService.graph(db, canonical_id, depth)
    return render_relation_graph(canonical_id, graph)
