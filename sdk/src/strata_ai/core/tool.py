from __future__ import annotations
import inspect
from typing import Any, Callable, Dict, Optional, get_type_hints, overload
from pydantic import BaseModel


# Overloads for static type checking
@overload
def tool(
    fn: None = ...,
    *,
    name: Optional[str] = ...,
    description: str = ...,
    requires_approval: bool = ...,
    pii_sensitive: bool = ...,
) -> Callable[[Callable[..., Any]], Tool]: ...


@overload
def tool(
    fn: Callable[..., Any],
    *,
    name: Optional[str] = ...,
    description: str = ...,
    requires_approval: bool = ...,
    pii_sensitive: bool = ...,
) -> Tool: ...


def tool(
    fn: Optional[Callable[..., Any]] = None,
    *,
    name: Optional[str] = None,
    description: str = "",
    requires_approval: bool = False,
    pii_sensitive: bool = False,
) -> Callable | Tool:
    """Decorator that turns a function into a Tool object."""

    def decorator(func: Callable[..., Any]) -> Tool:
        tool_name = name or func.__name__
        schema = _extract_json_schema(func)
        return Tool(
            name=tool_name,
            description=description,
            fn=func,
            input_schema=schema,  # Renamed to avoid BaseModel.schema collision
            requires_approval=requires_approval,
            pii_sensitive=pii_sensitive,
        )

    if fn is not None:
        return decorator(fn)
    return decorator


class Tool(BaseModel):
    name: str
    description: str
    fn: Callable[..., Any]
    input_schema: Dict[str, Any]  # Renamed field
    requires_approval: bool = False
    pii_sensitive: bool = False
    model_config = {"arbitrary_types_allowed": True}

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.fn(*args, **kwargs)


def _extract_json_schema(func: Callable[..., Any]) -> Dict[str, Any]:
    sig = inspect.signature(func)
    hints = get_type_hints(func)
    properties: Dict[str, Any] = {}
    required: list[str] = []

    type_map = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object",
    }

    for param_name, param in sig.parameters.items():
        if param_name in ("self", "cls", "kwargs"):
            continue

        param_type = hints.get(param_name, Any)
        is_required = param.default is inspect.Parameter.empty
        if is_required:
            required.append(param_name)

        base_type = type_map.get(param_type, "string")
        properties[param_name] = {"type": base_type}
        if not is_required:
            properties[param_name]["default"] = param.default

    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }
