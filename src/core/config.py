import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
NOTION_API_KEY = os.getenv("NOTION_API_KEY", "")
NOTION_VERSION = os.getenv("NOTION_VERSION", "2022-06-28")
NOTION_ROOT_PAGE = os.getenv("NOTION_ROOT_PAGE", "")

if not OPENAI_API_KEY:
    print("WARNING: OPENAI_API_KEY not set in .env file")
    print("Set it in .env before running generate or other AI commands.")
    print()
if not NOTION_API_KEY:
    print("WARNING: NOTION_API_KEY not set in .env file")
    print("Set it in .env before running notion commands.")
    print()

# SQLAlchemy session provider for CLI
def get_db():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    db_url = os.getenv("DATABASE_URL")
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    return Session()
