def semantic_representation(entity):
    data = getattr(entity, 'data', {})
    return " ".join([
        data.get("title", ""),
        data.get("description", ""),
        " ".join(data.get("tags", [])),
        data.get("status", ""),
        data.get("priority", ""),
    ])

from openai import OpenAI
client = OpenAI()

def generate_embedding(text: str) -> list[float]:
    response = client.embeddings.create(
        model="text-embedding-3-large",
        input=text
    )
    return response.data[0].embedding

from models.entity_embedding import EntityEmbedding
from datetime import datetime

def update_embedding_for_entity(db, entity):
    text = semantic_representation(entity)
    embedding = generate_embedding(text)
    existing = db.query(EntityEmbedding).filter_by(entity_id=entity.id).one_or_none()
    if existing:
        existing.embedding = embedding
        existing.updated_at = datetime.utcnow()
    else:
        new = EntityEmbedding(entity_id=entity.id, embedding=embedding)
        db.add(new)
    db.commit()
