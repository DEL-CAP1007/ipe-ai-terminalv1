from services.relationship_service import RelationshipService
from cli.renderers import render_relations
from db.session import get_session

def relations_get_command(args):
    if not args:
        return "Usage: relations.get <canonical_id>"
    canonical_id = args[0]
    with get_session() as db:
        from_rels, to_rels = RelationshipService.get_relations_for_entity(db, canonical_id)
    return render_relations(canonical_id, from_rels, to_rels)
