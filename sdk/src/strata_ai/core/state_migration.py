from typing import Dict, Any, Callable
from strata_ai.core.exceptions import CheckpointStateError

MigrationFn = Callable[[Dict[str, Any]], Dict[str, Any]]


class StateMigrationRegistry:
    _registry: Dict[str, MigrationFn] = {}

    @classmethod
    def register(cls, from_v: str, to_v: str, fn: MigrationFn) -> None:
        cls._registry[f"{from_v}→{to_v}"] = fn

    @classmethod
    def reset(cls) -> None:
        cls._registry = {}

    @classmethod
    def migrate(cls, raw: Dict[str, Any], from_v: str, to_v: str) -> Dict[str, Any]:
        current = from_v
        while current != to_v:
            try:
                next_num = int(current.lstrip("v")) + 1
            except ValueError:
                raise CheckpointStateError(f"Invalid version format: {current}")
            next_v = f"v{next_num}"
            key = f"{current}→{next_v}"
            if key not in cls._registry:
                raise CheckpointStateError(
                    f"No migration path from {current} to {to_v}. Missing: {key}"
                )
            raw = cls._registry[key](raw)
            current = next_v
        return raw
