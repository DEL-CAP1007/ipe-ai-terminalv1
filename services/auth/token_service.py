import secrets
import hashlib
from datetime import datetime, timedelta
from models.api_token import ApiToken
from services.auth.authorization import AuthorizationService
from services.auth.identity import Identity

class TokenService:
    @staticmethod
    def generate_token():
        # 256-bit random
        token = secrets.token_urlsafe(48)
        return token

    @staticmethod
    def hash_token(raw):
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    @staticmethod
    def create_token(db, identity, scopes, description=None, ttl_hours=None):
        from services.audit.service import AuditService
        AuthorizationService.check(db, identity, "token.create")
        raw = TokenService.generate_token()
        hashed = TokenService.hash_token(raw)
        expires_at = None
        if ttl_hours:
            expires_at = datetime.utcnow() + timedelta(hours=ttl_hours)
        token_row = ApiToken(
            token_hash=hashed,
            owner_user_id=(identity.subject_id if identity.subject_type=="user" else None),
            owner_service_id=(identity.subject_id if identity.subject_type=="service_account" else None),
            scopes=scopes,
            description=description,
            expires_at=expires_at
        )
        db.add(token_row)
        db.commit()
        AuditService.log(
            db,
            identity=identity,
            action="token.create",
            target_type="token",
            target_id=str(token_row.id),
            target_label=description,
            metadata={"scopes": scopes, "expires_at": token_row.expires_at},
            status="success",
        )
        return raw  # Only returned once

    @staticmethod
    def resolve_token(db, raw_token):
        hashed = TokenService.hash_token(raw_token)
        token = db.query(ApiToken).filter_by(token_hash=hashed).one_or_none()
        if not token:
            return None
        if token.expires_at and token.expires_at < datetime.utcnow():
            return None
        token.last_used_at = datetime.utcnow()
        db.commit()
        # Build an identity
        if token.owner_user_id:
            subject = Identity(
                subject_type="user",
                subject_id=str(token.owner_user_id),
                display_name="(token user)",
            )
        else:
            subject = Identity(
                subject_type="service_account",
                subject_id=str(token.owner_service_id),
                display_name="(token service)",
            )
        subject.token_scopes = token.scopes
        return subject
