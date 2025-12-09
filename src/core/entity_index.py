import uuid
from datetime import datetime
from typing import List

class EntityIndex:
    def __init__(self, entity_id, entity_type, canonical_id, title, summary, tags, status, priority, assignee, owner, due_date, updated_at, search_vector):
        self.id = str(uuid.uuid4())
        self.entity_id = entity_id
        self.entity_type = entity_type
        self.canonical_id = canonical_id
        self.title = title
        self.summary = summary
        self.tags = tags
        self.status = status
        self.priority = priority
        self.assignee = assignee
        self.owner = owner
        self.due_date = due_date
        self.updated_at = updated_at
        self.search_vector = search_vector

    def to_dict(self):
        return self.__dict__

# In-memory index for demo purposes
entity_index_db: List[EntityIndex] = []

# Build index record from canonical entity

def build_index_record(entity):
    data = entity.data
    etype = getattr(entity, 'entity_type', None) or data.get('entity_type')
    if etype == "task":
        title = data.get("title")
        summary = data.get("description")
        tags = data.get("tags", [])
        status = data.get("status")
        priority = data.get("priority")
        assignee = data.get("assignee")
        owner = None
        due_date = data.get("due_date")
    elif etype == "pipeline":
        title = data.get("name")
        summary = data.get("description")
        tags = data.get("tags", [])
        status = data.get("status")
        priority = None
        assignee = None
        owner = data.get("owner")
        due_date = None
    else:
        title = data.get("title") or data.get("name") or getattr(entity, 'canonical_id', None)
        summary = data.get("description") or ""
        tags = data.get("tags", [])
        status = data.get("status")
        priority = data.get("priority")
        assignee = data.get("assignee")
        owner = data.get("owner")
        due_date = data.get("due_date")
    full_text = " ".join([
        str(title or ""),
        str(summary or ""),
        " ".join(tags or []),
        str(status or ""),
        str(priority or ""),
    ])
    search_vector = full_text.lower()  # Simple for demo; replace with tsvector in production
    return EntityIndex(
        entity_id=getattr(entity, 'id', None),
        entity_type=etype,
        canonical_id=getattr(entity, 'canonical_id', None),
        title=title,
        summary=summary,
        tags=tags,
        status=status,
        priority=priority,
        assignee=assignee,
        owner=owner,
        due_date=due_date,
        updated_at=getattr(entity, 'last_modified', datetime.utcnow().isoformat()),
        search_vector=search_vector
    )

def update_index_for_entity(entity):
    index_record = build_index_record(entity)
    # Remove old index for this entity_id
    global entity_index_db
    entity_index_db = [r for r in entity_index_db if r.entity_id != index_record.entity_id]
    entity_index_db.append(index_record)

# Query engine

def query_entities(entity_type=None, filters=None, tags=None, search_text=None, limit=50, sort_field=None, sort_dir="desc"):
    results = entity_index_db
    if entity_type:
        results = [r for r in results if r.entity_type == entity_type]
    if filters:
        for k, v in filters.items():
            results = [r for r in results if getattr(r, k, None) == v]
    if tags:
        results = [r for r in results if set(tags).issubset(set(r.tags))]
    if search_text:
        results = [r for r in results if search_text.lower() in r.search_vector]
    if sort_field:
        results = sorted(results, key=lambda r: getattr(r, sort_field, None), reverse=(sort_dir=="desc"))
    return results[:limit]
