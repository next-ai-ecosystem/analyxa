"""Prompt Generator — Converts schema + conversation into LLM-ready prompts."""

import json

_DEFAULT_SYSTEM_CONTEXT = (
    "You are a conversation analysis engine. Your task is to extract structured "
    "information from conversations between users and AI agents. Be precise, "
    "evidence-based, and avoid speculation."
)

_DEFAULT_OUTPUT_FORMAT = (
    "Respond with a single valid JSON object. No markdown, no code fences, "
    "no explanatory text before or after the JSON. Every required field must be present. "
    "Optional fields should be included only if there is clear evidence."
)


def build_prompt(schema: dict, conversation: str, context: dict | None = None) -> dict:
    """Build a {system, user} prompt pair from a schema and conversation.

    Args:
        schema: Fully resolved schema dict (output of SchemaManager.load_schema()).
        conversation: Raw conversation text to analyze.
        context: Optional additional context. Supported keys: agent_name, agent_type,
                 company, language, or any arbitrary key:value pair.

    Returns:
        dict with keys "system" (str) and "user" (str).
    """
    prompt_cfg = schema.get("prompt") or {}
    fields = schema["fields"]

    system_sections = []

    # Section 1 — Role
    system_sections.append(
        prompt_cfg.get("system_context", _DEFAULT_SYSTEM_CONTEXT).strip()
    )

    # Section 2 — Additional context (only if context provided and non-empty)
    if context:
        context_str = _format_context(context)
        if context_str:
            system_sections.append(context_str)

    # Section 3 — Multi-language instructions
    system_sections.append(
        "LANGUAGE INSTRUCTIONS (CRITICAL — follow exactly):\n"
        '1. Detect the primary language of the conversation text.\n'
        '2. Set the "language" field to the ISO 639-1 code (e.g., "es", "en", "fr", "pt", "de", "it", "ja", "zh").\n'
        '3. Generate ALL string and array field VALUES in the detected language. '
        'For example, if the conversation is in Spanish, the "summary" value must be in Spanish, '
        '"topics" values must be in Spanish, etc.\n'
        '4. Field NAMES (JSON keys) must ALWAYS remain in English — never translate them. '
        'Use "sentiment", not "sentimiento".\n'
        '5. Boolean and numeric values are language-independent — do not translate them.\n'
        '6. For mixed-language conversations, use the dominant language (the one used most).\n'
        '7. If the language cannot be determined, set language to "und".'
    )

    # Section 4 — Field definitions
    field_lines = ["You must extract the following fields:\n"]
    for i, field in enumerate(fields, start=1):
        field_lines.append(_format_field_definition(i, field))
    system_sections.append("\n".join(field_lines))

    # Section 5 — Output format
    system_sections.append(
        prompt_cfg.get("output_format", _DEFAULT_OUTPUT_FORMAT).strip()
    )

    # Section 6 — Analysis guidelines
    guidelines = prompt_cfg.get("analysis_guidelines")
    if guidelines:
        lines = ["Analysis guidelines:"]
        for g in guidelines:
            lines.append(f"- {g}")
        system_sections.append("\n".join(lines))

    # Section 7 — JSON template
    template = _generate_json_template(fields)
    system_sections.append(f"Your response must follow this exact JSON structure:\n{template}")

    system_prompt = "\n\n".join(system_sections)

    # User prompt
    language = (context or {}).get("language")
    if language and language != "en":
        intro = (
            f"Analyze the following conversation and extract all fields as specified.\n"
            f"Respond in {language} for all free-text fields (title, summary, user_intent, action_items). "
            f"Use English for keyword fields."
        )
    else:
        intro = "Analyze the following conversation and extract all fields as specified."

    user_prompt = f"{intro}\n\nCONVERSATION:\n---\n{conversation}\n---\n\nRespond with the JSON object only."

    return {"system": system_prompt, "user": user_prompt}


def _format_field_definition(index: int, field: dict) -> str:
    """Format a single field as a numbered definition string.

    Args:
        index: 1-based position of the field.
        field: Field dict from schema.

    Returns:
        Formatted string describing the field for the LLM.
    """
    name = field["name"]
    ftype = field["type"]
    required = "required" if field.get("required") else "optional"
    description = field.get("description", "")
    hint = field.get("prompt_hint", "").strip()
    allowed = field.get("allowed_values")

    lines = [f"{index}. {name} ({ftype}, {required}): {description}"]
    if hint:
        lines.append(f"   Hint: {hint}")
    if allowed:
        lines.append(f"   Allowed values: {', '.join(allowed)}")

    return "\n".join(lines)


def _generate_json_template(fields: list) -> str:
    """Generate a JSON template string with type placeholders.

    Args:
        fields: List of field dicts from schema.

    Returns:
        JSON-formatted string with placeholder values per field type.
    """
    template: dict = {}
    for field in fields:
        name = field["name"]
        ftype = field["type"]
        allowed = field.get("allowed_values")

        if ftype == "string":
            template[name] = "string"
        elif ftype == "keyword":
            template[name] = "|".join(allowed) if allowed else "keyword"
        elif ftype == "keyword_array":
            template[name] = list(allowed[:2]) if allowed else ["keyword1", "keyword2"]
        elif ftype == "string_array":
            template[name] = ["string1", "string2"]
        elif ftype == "number":
            template[name] = 0
        elif ftype == "boolean":
            template[name] = True
        else:
            template[name] = "string"

    return json.dumps(template, indent=2)


def _format_context(context: dict) -> str:
    """Format context dict as a readable additional-context section.

    Args:
        context: Dict of context key:value pairs.

    Returns:
        Formatted string, or empty string if no non-None values.
    """
    lines = []
    for key, value in context.items():
        if value is None:
            continue
        label = key.replace("_", " ").title()
        lines.append(f"- {label}: {value}")

    if not lines:
        return ""

    return "Additional context for this analysis:\n" + "\n".join(lines)
