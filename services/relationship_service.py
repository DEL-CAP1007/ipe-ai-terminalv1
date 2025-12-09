from models.entity_relation import EntityRelation
from models.entity import Entity
from sqlalchemy.orm import Session

INVERSE_RELATIONS = {
    "belongs_to": "includes",
    "part_of": "contains",
    "related_to": "related_to",
    "subtask_of": "includes",
    "depends_on": "supports",
    "drives": "driven_by",
    "output_of": "produces",
    "owned_by": "owns",
}

class RelationshipService:
    @staticmethod
    def add_relation(db: Session, from_entity: Entity, to_entity: Entity, relation_type: str):
        rel = EntityRelation(
            from_entity_id=from_entity.id,
            from_type=from_entity.entity_type,
            from_canonical=from_entity.canonical_id,
            to_entity_id=to_entity.id,
            to_type=to_entity.entity_type,
            to_canonical=to_entity.canonical_id,
            relation_type=relation_type,
        )
            from services.audit.service import AuditService
            AuditService.log(
                db,
                identity=None,  # Pass actual identity if available
                action="entity.relation.add",
                target_type="entity",
                target_id=str(from_entity.id),
                target_label=f"{from_entity.entity_type}:{from_entity.id}",
                metadata={"to_entity": str(to_entity.id), "relation_type": relation_type},
                status="success",
            )
        db.add(rel)
        db.commit()
        RelationshipService.create_inverse_relation_if_needed(db, rel)
        return rel

    @staticmethod
    def create_inverse_relation_if_needed(db: Session, rel: EntityRelation):
        inverse_type = INVERSE_RELATIONS.get(rel.relation_type)
        if not inverse_type:
            return
        # Check if inverse already exists
        exists = db.query(EntityRelation).filter_by(
            from_entity_id=rel.to_entity_id,
            to_entity_id=rel.from_entity_id,
            relation_type=inverse_type
        ).first()
        if not exists:
            inverse = EntityRelation(
                from_entity_id=rel.to_entity_id,
                from_type=rel.to_type,
                from_canonical=rel.to_canonical,
                to_entity_id=rel.from_entity_id,
                to_type=rel.from_type,
                to_canonical=rel.from_canonical,
                relation_type=inverse_type,
            )
            db.add(inverse)
            db.commit()

    @staticmethod
    def get_relations_for_entity(db: Session, canonical_id: str):
        from_rels = db.query(EntityRelation).filter_by(from_canonical=canonical_id).all()
        to_rels = db.query(EntityRelation).filter_by(to_canonical=canonical_id).all()
        return from_rels, to_rels

    @staticmethod
    def find_relations(db: Session, relation_type: str, canonical_id: str):
        return db.query(EntityRelation).filter_by(relation_type=relation_type, to_canonical=canonical_id).all()

    @staticmethod
    def graph(db: Session, canonical_id: str, depth: int = 2):
        # Simple BFS for relationship graph
        visited = set()
        queue = [(canonical_id, 0)]
        graph = {}
        while queue:
            node, d = queue.pop(0)
            if d > depth or node in visited:
                continue
            visited.add(node)
            from_rels, _ = RelationshipService.get_relations_for_entity(db, node)
            graph[node] = [(r.relation_type, r.to_canonical) for r in from_rels]
            for _, target in graph[node]:
                queue.append((target, d + 1))
        return graph

    @staticmethod
    def audit(db: Session):
        # Orphan and broken link detection
        orphans = []
        broken = []
        # Example: tasks without client/event
        tasks = db.query(Entity).filter_by(entity_type="task").all()
        for t in tasks:
            from_rels, to_rels = RelationshipService.get_relations_for_entity(db, t.canonical_id)
            has_client = any(r.to_type == "client" for r in from_rels)
            has_event = any(r.to_type == "event" for r in from_rels)
            if not has_client and not has_event:
                orphans.append(t)
        # Broken links
        rels = db.query(EntityRelation).all()
        for r in rels:
            if not db.query(Entity).filter_by(canonical_id=r.to_canonical).first():
                broken.append(r)
        # Telemetry hook
        from services.telemetry_repository import TelemetryRepository
        import datetime
        TelemetryRepository.add(db, 'entity_relations', len(orphans) + len(broken), datetime.datetime.utcnow(), {'orphans': len(orphans), 'broken': len(broken)})
        return orphans, broken
