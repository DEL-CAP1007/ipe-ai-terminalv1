from sqlalchemy.orm import Session
from sqlalchemy import select, text
from models.entity_index import EntityIndex
from services.query_engine.models import QueryCriteria

class QueryService:
    @staticmethod
    def search(db: Session, criteria: QueryCriteria):
        query = select(EntityIndex)
        # Entity type filtering
        if criteria.entity_type:
            query = query.where(EntityIndex.entity_type == criteria.entity_type)
        # Field filters
        for field, value in (criteria.filters or {}).items():
            col = getattr(EntityIndex, field, None)
            if col is not None:
                query = query.where(col == value)
        # Tag filtering
        if criteria.tags:
            for tag in criteria.tags:
                query = query.where(text(f"'{tag}' = ANY(tags)"))
        # Dedicated fields
        if criteria.assignee:
            query = query.where(EntityIndex.assignee == criteria.assignee)
        if criteria.owner:
            query = query.where(EntityIndex.owner == criteria.owner)
        # Full-text search
        if criteria.search_text:
            ts_query = text(f"plainto_tsquery('simple', :search)")
            query = query.where(EntityIndex.search_vector.op('@@')(ts_query))
            query = query.params(search=criteria.search_text)
        # Sorting
        if criteria.sort_field:
            sort_col = getattr(EntityIndex, criteria.sort_field, None)
            if sort_col is not None:
                if criteria.sort_dir == "asc":
                    query = query.order_by(sort_col.asc())
                else:
                    query = query.order_by(sort_col.desc())
        else:
            query = query.order_by(EntityIndex.updated_at.desc())
        # Limit
        query = query.limit(criteria.limit)
        results = db.execute(query).scalars().all()
        return results
