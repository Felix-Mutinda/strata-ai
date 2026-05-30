import pytest
from strata_ai.core.state_migration import StateMigrationRegistry, CheckpointStateError


class TestStateMigration:
    def setup_method(self):
        StateMigrationRegistry.reset()

    def test_stepwise_migration(self):
        StateMigrationRegistry.register("v1", "v2", lambda r: {**r, "migrated": True})
        raw = {"messages": [], "status": "running"}
        result = StateMigrationRegistry.migrate(raw, "v1", "v2")
        assert result["migrated"] is True

    def test_missing_migration_raises(self):
        with pytest.raises(CheckpointStateError, match="Missing: v1→v2"):
            StateMigrationRegistry.migrate({}, "v1", "v2")

    def test_empty_messages_handled(self):
        StateMigrationRegistry.register("v1", "v2", lambda r: {**r, "messages": []})
        raw = {"messages": [], "status": "running"}
        result = StateMigrationRegistry.migrate(raw, "v1", "v2")
        assert result["messages"] == []
