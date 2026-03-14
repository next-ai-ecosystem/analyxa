"""CLI — Command-line interface for Analyxa using Click."""

import json
import sys
from pathlib import Path

import click


@click.group()
@click.version_option(package_name="analyxa")
def main():
    """Analyxa — Multi-dimensional extraction engine for AI conversations."""
    pass


# ------------------------------------------------------------------
# analyze command
# ------------------------------------------------------------------

@main.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--schema", "-s", default="universal", help="Schema to use for analysis")
@click.option("--output", "-o", default=None, help="Output file path (default: stdout)")
@click.option("--format", "-f", "output_format", type=click.Choice(["json", "compact"]), default="json", help="Output format")
@click.option("--provider", "-p", default=None, help="LLM provider (anthropic/openai)")
@click.option("--model", "-m", default=None, help="LLM model override")
@click.option("--no-embeddings", is_flag=True, help="Disable embedding generation")
@click.option("--context", "-c", multiple=True, help="Context key=value pairs (repeatable)")
def analyze(file, schema, output, output_format, provider, model, no_embeddings, context):
    """Analyze a conversation file and extract structured data."""
    try:
        from analyxa.config import get_config
        config = get_config()

        # Parse context key=value pairs
        ctx = {}
        for item in context:
            if "=" in item:
                key, value = item.split("=", 1)
                ctx[key] = value
        context_dict = ctx if ctx else None

        # Read conversation
        from analyxa.sources.file_source import FileSource
        source = FileSource(file)
        conversation = source.read()

        # Create analyzer and run
        from analyxa.analyzer import Analyzer
        analyzer = Analyzer(
            schema_name=schema,
            provider=provider or config.default_provider,
            model=model or config.default_model,
            enable_embeddings=not no_embeddings and config.enable_embeddings,
        )

        result = analyzer.analyze(conversation, context=context_dict)

        # Output
        if output_format == "compact":
            output_data = result.to_flat_dict()
        else:
            output_data = result.to_dict()

        json_str = json.dumps(output_data, indent=2, ensure_ascii=False)

        if output:
            from analyxa.sinks.json_sink import JsonSink
            sink = JsonSink(output)
            sink.write(output_data)
            click.echo(f"✅ Analysis saved to {output}")
        else:
            click.echo(json_str)

    except FileNotFoundError as e:
        click.echo(f"❌ Schema '{schema}' not found.", err=True)
        sys.exit(1)
    except ValueError as e:
        click.echo(f"❌ {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Analysis failed: {e}", err=True)
        sys.exit(1)


# ------------------------------------------------------------------
# schemas group
# ------------------------------------------------------------------

@main.group()
def schemas():
    """Manage analysis schemas."""
    pass


@schemas.command("list")
def schemas_list():
    """List available schemas."""
    from analyxa.schema import SchemaManager
    sm = SchemaManager()
    names = sm.list_schemas()

    click.echo(f"Available schemas ({len(names)}):\n")
    for name in names:
        schema = sm.load_schema(name)
        meta = schema["metadata"]
        fields = schema["fields"]
        inherits = meta.get("inherits") or "—"
        click.echo(f"  {name}")
        click.echo(f"    Version: {meta['version']}  |  Fields: {len(fields)}  |  Inherits: {inherits}")
        click.echo(f"    {meta['description']}")
        click.echo()


@schemas.command("show")
@click.argument("name")
def schemas_show(name):
    """Show detailed schema information."""
    from analyxa.schema import SchemaManager
    sm = SchemaManager()

    try:
        schema = sm.load_schema(name)
    except FileNotFoundError:
        click.echo(f"❌ Schema '{name}' not found.", err=True)
        sys.exit(1)

    meta = schema["metadata"]
    fields = schema["fields"]

    click.echo(f"Schema: {meta['name']} v{meta['version']}")
    click.echo(f"Description: {meta['description']}")
    if meta.get("inherits"):
        click.echo(f"Inherits: {meta['inherits']}")
    click.echo(f"\nFields ({len(fields)}):\n")

    for i, field in enumerate(fields, 1):
        req = "required" if field.get("required") else "optional"
        ftype = field["type"]
        click.echo(f"  {i:2d}. {field['name']} ({ftype}, {req})")
        click.echo(f"      {field['description']}")
        if field.get("allowed_values"):
            click.echo(f"      Values: {', '.join(field['allowed_values'])}")
        click.echo()


# ------------------------------------------------------------------
# version command
# ------------------------------------------------------------------

@main.command()
def version():
    """Show Analyxa version and component status."""
    from analyxa import __version__
    from analyxa.config import get_config

    config = get_config()

    click.echo(f"Analyxa v{__version__}")
    click.echo(f"Provider: {config.default_provider}")
    click.echo(f"Model: {config.default_model or '(provider default)'}")
    click.echo(f"Schema: {config.default_schema}")
    click.echo(f"Embeddings: {'enabled' if config.enable_embeddings else 'disabled'}")
    click.echo(f"Anthropic API: {'configured' if config.anthropic_api_key else 'not set'}")
    click.echo(f"OpenAI API: {'configured' if config.openai_api_key else 'not set'}")
