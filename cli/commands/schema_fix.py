from services.schema_validator import SchemaValidatorService
from services.coercion import coerce_entity_data
from services.entities import EntityService
from cli.renderers import render_schema_validation_report

def schema_validate_command(args):
    etype = args[0] if args else None
    entities = EntityService.list_entities(entity_type=etype)
    invalid = []
    for e in entities:
        coerced = coerce_entity_data(e.entity_type, e.data)
        result = SchemaValidatorService.validate_entity(e.entity_type, coerced)
        if not result.valid:
            invalid.append((e, result.errors))
    return render_schema_validation_report(invalid)

def schema_fix_command(args):
    target = args[0] if args else None
    if not target:
        return "Usage: schema.fix <entity_type|canonical_id>"
    if target.upper().startswith("TASK-"):
        entities = [EntityService.get_by_canonical_id(target)]
    else:
        entities = EntityService.list_entities(entity_type=target)
    fixed = 0
    still_invalid = 0
    for e in entities:
        coerced = coerce_entity_data(e.entity_type, e.data)
        result = SchemaValidatorService.validate_entity(e.entity_type, coerced)
        if result.valid:
            e.data = result.data
            EntityService.save_entity(e)
            fixed += 1
        else:
            still_invalid += 1
    return f"Fixed: {fixed}, Still invalid: {still_invalid}"
