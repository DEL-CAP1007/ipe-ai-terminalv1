from dataclasses import dataclass
from typing import Optional, Dict, List

@dataclass
class QueryCriteria:
    entity_type: Optional[str] = None       # "task", "pipeline", "any"
    filters: Dict[str, str] = None          # field:value pairs
    tags: List[str] = None                  # tag filters
    search_text: Optional[str] = None       # full-text search
    semantic_text: Optional[str] = None     # semantic search text
    limit: int = 50                         # default limit
    sort_field: Optional[str] = None
    sort_dir: Optional[str] = "desc"         # asc|desc
    assignee: Optional[str] = None          # dedicated filter
    owner: Optional[str] = None
