"""SchemaManager — Loads, validates, resolves inheritance, and caches YAML schemas."""

from pathlib import Path

import yaml


class SchemaManager:
    """Manages Analyxa schemas: loading, inheritance resolution, validation, and caching."""

    def __init__(self, schemas_dir: "str | Path | None" = None):
        if schemas_dir is None:
            self._schemas_dir = Path(__file__).parent / "schemas"
        else:
            self._schemas_dir = Path(schemas_dir)
        self._cache: dict = {}

    def load_schema(self, name: str) -> dict:
        """Load a schema by name, resolving inheritance and using cache.

        Args:
            name: Schema name without .yaml extension (e.g., "universal", "support").

        Returns:
            Fully resolved schema dict (with inheritance applied).

        Raises:
            FileNotFoundError: If the schema file does not exist.
            ValueError: If the YAML is invalid or missing required sections.
        """
        if name in self._cache:
            return self._cache[name]

        schema_path = self._schemas_dir / f"{name}.yaml"
        if not schema_path.exists():
            raise FileNotFoundError(
                f"Schema '{name}' not found. Expected file: {schema_path}"
            )

        with open(schema_path, "r", encoding="utf-8") as f:
            schema = yaml.safe_load(f)

        if not isinstance(schema, dict):
            raise ValueError(f"Schema '{name}': YAML must be a mapping, got {type(schema)}")
        if "metadata" not in schema:
            raise ValueError(f"Schema '{name}': missing required section 'metadata'")
        if "fields" not in schema:
            raise ValueError(f"Schema '{name}': missing required section 'fields'")

        parent_name = schema["metadata"].get("inherits")
        if parent_name:
            parent = self.load_schema(parent_name)
            schema = self._resolve_inheritance(schema, parent)

        self._cache[name] = schema
        return schema

    def _resolve_inheritance(self, child: dict, parent: dict) -> dict:
        """Merge child schema with parent, parent fields come first.

        Args:
            child: Child schema dict (already parsed, not yet in cache).
            parent: Parent schema dict (fully resolved).

        Returns:
            New schema dict with inheritance applied.
        """
        resolved = {}
        resolved["metadata"] = child["metadata"]
        resolved["fields"] = list(parent["fields"]) + list(child["fields"])
        resolved["auto_fields"] = child.get("auto_fields") or parent.get("auto_fields")
        resolved["prompt"] = child.get("prompt") or parent.get("prompt")
        return resolved

    def list_schemas(self) -> list:
        """Return sorted list of schema names available in schemas_dir."""
        return sorted(
            p.stem for p in self._schemas_dir.glob("*.yaml")
        )

    def get_field_names(self, name: str) -> list:
        """Return ordered list of field names for a schema.

        Args:
            name: Schema name.

        Returns:
            List of field name strings in schema order.
        """
        schema = self.load_schema(name)
        return [field["name"] for field in schema["fields"]]

    def validate_result(self, name: str, result: dict) -> "tuple[bool, list[str]]":
        """Validate an extraction result against a schema.

        Checks:
        - All required fields are present.
        - Keyword fields have values within allowed_values.
        - Basic type correctness (keyword→str, keyword_array→list, boolean→bool, etc.).

        Args:
            name: Schema name.
            result: The dict to validate (LLM extraction output).

        Returns:
            (is_valid, errors): is_valid is True when errors is empty.
        """
        schema = self.load_schema(name)
        errors = []

        type_checks = {
            "string": str,
            "keyword": str,
            "keyword_array": list,
            "string_array": list,
            "number": (int, float),
            "boolean": bool,
        }

        for field in schema["fields"]:
            field_name = field["name"]
            required = field.get("required", False)
            field_type = field.get("type")
            allowed = field.get("allowed_values")

            if field_name not in result:
                if required:
                    errors.append(f"Missing required field: {field_name}")
                continue

            value = result[field_name]

            expected_python_type = type_checks.get(field_type)
            if expected_python_type and not isinstance(value, expected_python_type):
                errors.append(
                    f"Invalid type for {field_name}: expected {field_type}, "
                    f"got {type(value).__name__}"
                )
                continue

            if allowed and field_type == "keyword":
                if value not in allowed:
                    errors.append(
                        f"Invalid value for {field_name}: '{value}' not in {allowed}"
                    )

            if allowed and field_type == "keyword_array":
                for v in value:
                    if v not in allowed:
                        errors.append(
                            f"Invalid value for {field_name}: '{v}' not in {allowed}"
                        )

        is_valid = len(errors) == 0
        return is_valid, errors
