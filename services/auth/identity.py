from dataclasses import dataclass
from typing import Optional

@dataclass
class Identity:
    subject_type: str              # "user" or "service_account"
    subject_id: str
    display_name: str
    email: Optional[str] = None
    name: Optional[str] = None     # for service accounts

def get_current_identity(db, session_id) -> Optional[Identity]:
    from services.auth.service import AuthService
    raw = AuthService.get_identity_from_session(db, session_id)
    if not raw:
        return None
    if raw["type"] == "user":
        return Identity(
            subject_type="user",
            subject_id=raw["id"],
            display_name=raw["display_name"],
            email=raw["email"],
        )
    else:
        return Identity(
            subject_type="service_account",
            subject_id=raw["id"],
            display_name=raw["name"],
            name=raw["name"],
        )
