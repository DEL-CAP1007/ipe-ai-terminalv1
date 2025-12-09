from services.relationship_service import RelationshipService
from models.entity import Entity
from sqlalchemy.orm import Session

class AgentRelationshipAPI:
    @staticmethod
    def get_all_relations(db: Session, entity: Entity):
        from_rels, to_rels = RelationshipService.get_relations_for_entity(db, entity.canonical_id)
        return {
            "outgoing": [(r.relation_type, r.to_canonical) for r in from_rels],
            "incoming": [(r.relation_type, r.from_canonical) for r in to_rels],
        }

    @staticmethod
    def trace_dependencies(db: Session, entity: Entity, max_depth: int = 3):
        graph = RelationshipService.graph(db, entity.canonical_id, depth=max_depth)
        return graph

    @staticmethod
    def get_context(db: Session, entity: Entity):
        # Fetch upstream and downstream context for reasoning
        graph = RelationshipService.graph(db, entity.canonical_id, depth=2)
        context = set()
        for node, edges in graph.items():
            context.add(node)
            for _, target in edges:
                context.add(target)
        return list(context)

    @staticmethod
    def find_related_entities(db: Session, entity: Entity, relation_type: str):
        rels = RelationshipService.find_relations(db, relation_type, entity.canonical_id)
        return [db.query(Entity).filter_by(canonical_id=r.to_canonical).first() for r in rels]
