def render_relations(canonical_id, from_rels, to_rels):
    lines = [f"=== Relationships for {canonical_id} ==="]
    lines.append("Outgoing:")
    for r in from_rels:
        lines.append(f"- {r.relation_type} {r.to_canonical} ({getattr(r.to_entity, 'title', '')})")
    lines.append("Incoming:")
    for r in to_rels:
        lines.append(f"- {r.relation_type} {r.from_canonical} ({getattr(r.from_entity, 'title', '')})")
    return "\n".join(lines)

def render_relation_find(relation_type, canonical_id, rels):
    lines = [f"=== {relation_type} relations for {canonical_id} ==="]
    for r in rels:
        lines.append(f"- {r.from_canonical} → {r.to_canonical}")
    return "\n".join(lines)

def render_relation_graph(canonical_id, graph):
    lines = [f"=== Relationship Graph for {canonical_id} ==="]
    def recurse(node, depth, prefix):
        if depth > 0:
            for rel_type, target in graph.get(node, []):
                lines.append(f"{prefix}{node} ──{rel_type}→ {target}")
                recurse(target, depth - 1, prefix + "    ")
    recurse(canonical_id, 2, "")
    return "\n".join(lines)

def render_relation_audit(orphans, broken):
    lines = ["=== Relationship Audit ==="]
    if orphans:
        lines.append("Orphans:")
        for o in orphans:
            lines.append(f"  {getattr(o, 'canonical_id', '')} (no client, no event)")
    if broken:
        lines.append("Broken links:")
        for b in broken:
            lines.append(f"  {b.from_canonical} → {b.to_canonical} (target not found)")
    return "\n".join(lines)
