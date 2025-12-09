from datetime import datetime
from models.audit_log import AuditLog

class AuditService:
    @staticmethod
    def log(
        db,
        *,
        identity,
        action: str,
        target_type: str = None,
        target_id: str = None,
        target_label: str = None,
        metadata: dict = None,
        status: str = "success",
        error_message: str = None,
    ):
        actor_type = identity.subject_type if identity else "anonymous"
        actor_id = identity.subject_id if identity else "unknown"
        actor_label = getattr(identity, "display_name", None) if identity else "unknown"
        # include token info if present
        if hasattr(identity, "token_id"):
            actor_type = "token"
            actor_id = identity.token_id
            actor_label = f"token:{identity.token_id}"
        entry = AuditLog(
            actor_type=actor_type,
            actor_id=str(actor_id),
            actor_label=actor_label,
            action=action,
            target_type=target_type,
            target_id=target_id,
            target_label=target_label,
            metadata=metadata or {},
            status=status,
            error_message=error_message,
            created_at=datetime.utcnow()
        )
        db.add(entry)
        db.commit()
