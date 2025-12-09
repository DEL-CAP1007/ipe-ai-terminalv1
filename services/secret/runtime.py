from db.session import get_session
from services.secret.service import SecretService
from services.auth.identity import Identity

SYSTEM_IDENTITY = Identity(
    subject_type="service_account",
    subject_id="SYSTEM",
    display_name="system"
)

def get_secret_value(name: str) -> str:
    with get_session() as db:
        return SecretService.get_secret(db, SYSTEM_IDENTITY, name)
