import datetime
from models.trigger import Trigger, TriggerRun
from services.trigger_repository import TriggerRepository
from sqlalchemy.orm import Session

class EventBus:
    def __init__(self, db: Session):
        self.db = db

    def emit(self, event_type: str, payload: dict):
        # Find enabled triggers for this event
        triggers = TriggerRepository.get_enabled_for_event(self.db, event_type)
        for trigger in triggers:
            TriggerEngine.evaluate(self.db, trigger, event_type, payload)
        # Telemetry hook
        from services.telemetry_repository import TelemetryRepository
        import datetime
        TelemetryRepository.add(self.db, 'events', 1, datetime.datetime.utcnow(), {'event_type': event_type})

class TriggerEngine:
    @staticmethod
    def evaluate(db: Session, trigger: Trigger, event_type: str, payload: dict):
        # Evaluate condition (assume Python expression in trigger.condition)
        context = dict(payload)
        try:
            if trigger.condition:
                result = eval(trigger.condition, {}, context)
            else:
                result = True
        except Exception:
            result = False
        # If condition passes, execute action
        if result:
            TriggerEngine.execute_action(db, trigger, event_type, payload)

    @staticmethod
    def execute_action(db: Session, trigger: Trigger, event_type: str, payload: dict):
        run = TriggerRun(
            trigger_id=trigger.id,
            event_type=event_type,
            started_at=datetime.datetime.utcnow(),
            status='running',
            payload=payload
        )
        db.add(run)
        db.commit()
        # Execute action (assume Python code in trigger.action)
        context = dict(payload)
        context['db'] = db
        context['trigger'] = trigger
        context['run'] = run
        try:
            if trigger.action:
                exec(trigger.action, {}, context)
            run.status = 'success'
        except Exception as e:
            run.status = 'error'
            run.error_message = str(e)
        run.finished_at = datetime.datetime.utcnow()
        db.commit()
        # Telemetry hook
        from services.telemetry_repository import TelemetryRepository
        TelemetryRepository.add(db, 'trigger_runs', 1, datetime.datetime.utcnow(), {'trigger_id': trigger.id, 'status': run.status})
