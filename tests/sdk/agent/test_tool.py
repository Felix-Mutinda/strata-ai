from typing import Dict
from strata_ai.core.tool import tool


class TestToolDecorator:
    def test_generates_schema_from_type_hints(self):
        @tool
        def search_db(query: str, limit: int = 10) -> Dict[str, str]:
            return {"result": "found"}

        assert search_db.name == "search_db"
        assert search_db.description == ""
        # Updated to input_schema
        assert search_db.input_schema["properties"]["query"]["type"] == "string"
        assert search_db.input_schema["properties"]["limit"]["type"] == "integer"
        assert "limit" not in search_db.input_schema["required"]

    def test_accepts_custom_name_and_description(self):
        @tool(name="custom_search", description="Searches external DB")
        def search_db(query: str) -> Dict:
            return {}

        assert search_db.name == "custom_search"
        assert search_db.description == "Searches external DB"

    def test_is_callable_and_executes_wrapped_fn(self):
        @tool
        def add(a: int, b: int) -> int:
            return a + b

        assert add(2, 3) == 5
