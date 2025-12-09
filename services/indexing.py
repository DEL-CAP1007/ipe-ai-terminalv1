from models.entity import Entity
from models.entity_index import EntityIndex
from sqlalchemy.orm import Session
from datetime import datetime

class EntityIndexBuilder:
    def __init__(self, db: Session):
        self.db = db

    def build_index_for_entity(self, entity: Entity):
        # Build or update index for a single entity
        index = self.db.query(EntityIndex).filter_by(entity_id=entity.id).first()
        if not index:
            index = EntityIndex(entity_id=entity.id)
        index.entity_type = entity.entity_type
        index.canonical_id = entity.canonical_id
        index.title = entity.title
        index.summary = entity.summary
        index.tags = entity.tags
        index.status = entity.status
        index.priority = entity.priority
        index.assignee = entity.assignee
        index.owner = entity.owner
        index.due_date = entity.due_date
        index.updated_at = entity.updated_at or datetime.utcnow()
        # Optionally set search_vector here
        self.db.add(index)
        self.db.commit()
        return index

    def rebuild_all_indexes(self):
        entities = self.db.query(Entity).all()
        for entity in entities:
            self.build_index_for_entity(entity)
