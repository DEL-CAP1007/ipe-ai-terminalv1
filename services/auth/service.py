from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models.user import User
from models.session import Session as SessionModel
from services.auth.passwords import verify_password

SESSION_TTL_HOURS = 12

class AuthService:
    @staticmethod
    def login(db: Session, email: str, password: str, user_agent: str = None, client_ip: str = None) -> SessionModel:
        user = db.query(User).filter_by(email=email).one_or_none()
        if not user or not user.is_active:
            raise ValueError("Invalid credentials")
        if not user.password_hash or not verify_password(password, user.password_hash):
            raise ValueError("Invalid credentials")
        now = datetime.utcnow()
        session = SessionModel(
            user=user,
            created_at=now,
            last_active_at=now,
            expires_at=now + timedelta(hours=SESSION_TTL_HOURS),
            user_agent=user_agent,
            client_ip=client_ip,
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def get_identity_from_session(db: Session, session_id) -> dict | None:
        sess = db.query(SessionModel).filter_by(id=session_id).one_or_none()
        if not sess:
            return None
        now = datetime.utcnow()
        if sess.expires_at and sess.expires_at < now:
            return None
        sess.last_active_at = now
        db.commit()
        if sess.user:
            return {
                "type": "user",
                "id": str(sess.user.id),
                "email": sess.user.email,
                "display_name": sess.user.display_name,
            }
        if sess.service:
            return {
                "type": "service_account",
                "id": str(sess.service.id),
                "name": sess.service.name,
            }
        return None

    @staticmethod
    def logout(db: Session, session_id):
        db.query(SessionModel).filter_by(id=session_id).delete()
        db.commit()
