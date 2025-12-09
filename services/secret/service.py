from sqlalchemy.orm import Session
from models.secret import Secret
from services.secret.crypto import encrypt_secret, decrypt_secret
from services.auth.authorization import AuthorizationService

class SecretService:
    @staticmethod
    def set_secret(db: Session, identity, name: str, value: str, scope: str = "system", description: str = None):
        from services.audit.service import AuditService
        AuthorizationService.check(db, identity, "secret.create")
        enc = encrypt_secret(value)
        secret = db.query(Secret).filter_by(name=name).one_or_none()
        action = "secret.set"
        status = "success"
        error_message = None
        try:
            if secret:
                AuthorizationService.check(db, identity, "secret.update")
                secret.value_encrypted = enc
                secret.description = description or secret.description
            else:
                secret = Secret(
                    name=name,
                    value_encrypted=enc,
                    scope=scope,
                    description=description,
                    owner_user_id=(identity.subject_id if scope == "user" and identity.subject_type == "user" else None),
                    owner_service_id=(identity.subject_id if scope == "service" and identity.subject_type == "service_account" else None),
                )
                db.add(secret)
            db.commit()
        except Exception as exc:
            status = "error"
            error_message = str(exc)
            raise
        finally:
            AuditService.log(
                db,
                identity=identity,
                action=action,
                target_type="secret",
                target_id=name,
                target_label=name,
                metadata={"scope": scope},
                status=status,
                error_message=error_message,
            )
        return secret

    @staticmethod
    def get_secret(db: Session, identity, name: str) -> str:
        AuthorizationService.check(db, identity, "secret.read")
        secret = db.query(Secret).filter_by(name=name).one_or_none()
        if not secret:
            raise ValueError(f"Secret '{name}' not found")
        return decrypt_secret(secret.value_encrypted)

    @staticmethod
    def delete_secret(db: Session, identity, name: str):
        from services.audit.service import AuditService
        AuthorizationService.check(db, identity, "secret.delete")
        secret = db.query(Secret).filter_by(name=name).one_or_none()
        status = "success"
        error_message = None
        try:
            if not secret:
                return False
            db.delete(secret)
            db.commit()
        except Exception as exc:
            status = "error"
            error_message = str(exc)
            raise
        finally:
            AuditService.log(
                db,
                identity=identity,
                action="secret.delete",
                target_type="secret",
                target_id=name,
                target_label=name,
                metadata={},
                status=status,
                error_message=error_message,
            )
        return True

    @staticmethod
    def list_secrets(db: Session, identity):
        AuthorizationService.check(db, identity, "secret.list")
        secrets = db.query(Secret).all()
        return [
            {
                "name": s.name,
                "scope": s.scope,
                "description": s.description,
                "updated_at": s.updated_at,
            }
            for s in secrets
        ]
