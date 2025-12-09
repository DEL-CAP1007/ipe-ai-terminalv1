from models.trigger import Trigger, TriggerRun
from sqlalchemy.orm import Session

class TriggerRepository:
    @staticmethod
    def get_enabled_for_event(db: Session, event_type: str):
        return db.query(Trigger).filter_by(event_type=event_type, is_enabled=True).all()

    @staticmethod
    def get_by_id(db: Session, trigger_id):
        return db.query(Trigger).filter_by(id=trigger_id).first()

    @staticmethod
    def list_all(db: Session):
        return db.query(Trigger).all()

    @staticmethod
    def add(db: Session, trigger: Trigger):
        db.add(trigger)
        db.commit()
        return trigger

    @staticmethod
    def remove(db: Session, trigger_id):
        t = db.query(Trigger).filter_by(id=trigger_id).first()
        if t:
            db.delete(t)
            db.commit()

    @staticmethod
    def enable(db: Session, trigger_id):
        t = db.query(Trigger).filter_by(id=trigger_id).first()
        if t:
            t.is_enabled = True
            db.commit()

    @staticmethod
    def disable(db: Session, trigger_id):
        t = db.query(Trigger).filter_by(id=trigger_id).first()
        if t:
            t.is_enabled = False
            db.commit()

    @staticmethod
    def get_runs(db: Session, trigger_id):
        return db.query(TriggerRun).filter_by(trigger_id=trigger_id).order_by(TriggerRun.started_at.desc()).all()
