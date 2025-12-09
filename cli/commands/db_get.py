from services.entities import EntityService
from cli.renderers import render_entity_card

def db_get_command(args):
    if not args:
        return "Usage: db.get <canonical_id>"
    canonical_id = args[0]
    entity = EntityService.get_by_canonical_id(canonical_id)
    if not entity:
        # Fuzzy suggestions
        suggestions = EntityService.suggest_canonical_ids(canonical_id)
        msg = f"Entity '{canonical_id}' not found."
        if suggestions:
            msg += "\nDid you mean:\n  " + "\n  ".join(suggestions)
            msg += f"\nTry:\n  query tasks --search \"{canonical_id}\""
        return msg
    return render_entity_card(entity)
