from typing import Type
from pydantic import ValidationError
from schemas.task import TaskSchema
from schemas.pipeline import PipelineSchema
from schemas.client import ClientSchema

ENTITY_SCHEMAS: dict[str, Type] = {
    "task": TaskSchema,
    "pipeline": PipelineSchema,
    "client": ClientSchema,
}

class SchemaValidationResult:
    def __init__(self, valid: bool, data=None, errors=None):
        self.valid = valid
        self.data = data  # normalized data
        self.errors = errors or []

class SchemaValidatorService:
    @staticmethod
    def validate_entity(entity_type: str, data: dict) -> SchemaValidationResult:
        schema_cls = ENTITY_SCHEMAS.get(entity_type)
        if not schema_cls:
            return SchemaValidationResult(valid=True, data=data)
        try:
            model = schema_cls(**data)
            return SchemaValidationResult(valid=True, data=model.dict())
        except ValidationError as e:
            # Telemetry hook for schema violations
            from services.telemetry_repository import TelemetryRepository
            import datetime
            TelemetryRepository.add(
                getattr(data, 'db', None),
                'schema_violations',
                len(e.errors()),
                datetime.datetime.utcnow(),
                {'entity_type': entity_type}
            )
            return SchemaValidationResult(valid=False, errors=e.errors())
