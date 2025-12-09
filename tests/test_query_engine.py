import pytest
from cli.commands.query import query_command

# Smoke test scenarios
@pytest.mark.parametrize("args, expect_in", [
    (["tasks", "status:open"], "status: open"),
    (["tasks", "tag:phase14"], "tags: ['phase14']"),
    (["tasks", "status:in_progress", "tag:engine", "priority:high"], "priority: high"),
    (["any", "--search", "canonical sync engine"], "canonical sync engine"),
    (["pipelines", "--sort updated_at:asc", "--limit", "5"], "updated:"),
    (["clients", "status:nonexistent"], "No results."),
])
def test_query_smoke(args, expect_in):
    result = query_command(args)
    assert expect_in in result
