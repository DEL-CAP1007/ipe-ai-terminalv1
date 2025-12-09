
from dataclasses import dataclass, field
from typing import Any, Dict
import hashlib

@dataclass
class CanonicalRecord:
    id: str
    source: str
    last_modified: str
    data: Dict[str, Any] = field(default_factory=dict)
    hash: str = ""

    def compute_hash(self):
        # Hash based on id, last_modified, and data
        raw = f"{self.id}|{self.last_modified}|{str(self.data)}"
        return hashlib.sha256(raw.encode()).hexdigest()

    def as_envelope(self):
        return {
            "id": self.id,
            "source": self.source,
            "last_modified": self.last_modified,
            "data": self.data,
            "hash": self.hash or self.compute_hash()
        }

# Example normalization function

def normalize_notion_record(notion_record):
    # Convert a Notion record to CanonicalRecord
    rec = CanonicalRecord(
        id=notion_record.get('id', ''),
        source='notion',
        last_modified=notion_record.get('last_edited_time', ''),
        data=notion_record.get('properties', {})
    )
    rec.hash = rec.compute_hash()
    return rec

def normalize_t7_record(t7_record):
    # Convert a T7 record to CanonicalRecord
    rec = CanonicalRecord(
        id=t7_record.get('id', ''),
        source='t7',
        last_modified=t7_record.get('last_modified', ''),
        data=t7_record.get('data', {})
    )
    rec.hash = rec.compute_hash()
    return rec
