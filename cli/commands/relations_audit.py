from services.relationship_service import RelationshipService
from cli.renderers import render_relation_audit
from db.session import get_session

def relations_audit_command(args):
    with get_session() as db:
        orphans, broken = RelationshipService.audit(db)
    return render_relation_audit(orphans, broken)
