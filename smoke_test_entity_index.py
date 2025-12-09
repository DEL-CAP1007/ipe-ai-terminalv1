import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.sync_manager import SyncManager
from models.entity import Entity
from models.entity_index import EntityIndex
from services.indexing import EntityIndexBuilder

def smoke_test_entity_index():
    # Example: Use DATABASE_URL from env
    db_url = os.getenv('DATABASE_URL', 'postgresql://localhost/ipe_ai_terminal')
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    # Run sync and index update
    sync_manager = SyncManager(db_session=session)
    sync_manager.sync(mode='full')
    # Check index population
    count = session.query(EntityIndex).count()
    print(f"EntityIndex records: {count}")
    assert count > 0, "EntityIndex should be populated after sync"
    print("Smoke test passed: EntityIndex populated.")

if __name__ == "__main__":
    smoke_test_entity_index()
