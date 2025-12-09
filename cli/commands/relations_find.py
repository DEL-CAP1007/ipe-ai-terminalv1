from services.relationship_service import RelationshipService
from cli.renderers import render_relation_find
from db.session import get_session

def relations_find_command(args):
    if len(args) < 2:
        return "Usage: relations.find <type> <canonical_id>"
    relation_type, canonical_id = args[0], args[1]
    with get_session() as db:
        rels = RelationshipService.find_relations(db, relation_type, canonical_id)
    return render_relation_find(relation_type, canonical_id, rels)
