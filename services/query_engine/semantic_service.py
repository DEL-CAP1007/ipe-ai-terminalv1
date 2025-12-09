from sqlalchemy import text
from models.entity_index import EntityIndex
from models.entity_embedding import EntityEmbedding
from services.query_engine.embedding import generate_embedding

class SemanticQueryService:
    @staticmethod
    def semantic_search(db, text_query: str, limit: int = 20):
        query_embedding = generate_embedding(text_query)
        sql = text("""
            SELECT
                ei.id
            FROM entity_embedding ee
            JOIN entity_index ei ON ei.entity_id = ee.entity_id
            ORDER BY ee.embedding <=> :query_embedding
            LIMIT :limit
        """)
        rows = db.execute(sql, {
            "query_embedding": query_embedding,
            "limit": limit,
        }).fetchall()
        results = [db.get(EntityIndex, row[0]) for row in rows]
        return results

    @staticmethod
    def hybrid_search(db, criteria):
        # Step 1: Semantic search candidate set (top 100)
        semantic_results = SemanticQueryService.semantic_search(
            db,
            criteria.semantic_text,
            limit=100
        )
        # Step 2: Filter candidates with structured criteria
        filtered = []
        for r in semantic_results:
            if criteria.entity_type and r.entity_type != criteria.entity_type:
                continue
            match = True
            for field, value in (criteria.filters or {}).items():
                if getattr(r, field) != value:
                    match = False
                    break
            if match:
                filtered.append(r)
        return filtered[:criteria.limit]
