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
# batch command
# ------------------------------------------------------------------

@main.command()
@click.argument("directory", type=click.Path(exists=True))
@click.option("--schema", "-s", default="universal", help="Schema to use")
@click.option("--output-dir", "-o", default=None, help="Directory for result JSON files")
@click.option("--provider", "-p", default=None, help="LLM provider")
@click.option("--no-embeddings", is_flag=True, help="Disable embeddings")
@click.option("--to-qdrant", is_flag=True, help="Store results in Qdrant")
def batch(directory, schema, output_dir, provider, no_embeddings, to_qdrant):
    """Batch analyze all conversation files in a directory."""
    from pathlib import Path as _Path
    from analyxa.config import get_config
    from analyxa.batch import batch_analyze

    config = get_config()
    dir_path = _Path(directory)
    txt_files = sorted(dir_path.glob("*.txt"))

    if not txt_files:
        click.echo(f"❌ No .txt files found in {directory}", err=True)
        sys.exit(1)

    conversations = []
    for f in txt_files:
        conversations.append({"text": f.read_text(encoding="utf-8"), "id": f.stem})

    sink = None
    if to_qdrant:
        from analyxa.sinks.qdrant_sink import QdrantSink
        sink = QdrantSink()
    elif output_dir:
        _Path(output_dir).mkdir(parents=True, exist_ok=True)

    def _progress(current, total, result):
        status = "✅" if result and result.validation_errors == [] else "⚠️" if result else "❌"
        click.echo(f"  [{current}/{total}] {status}", err=True)

    # Per-file JsonSink if output_dir (no single sink for directory mode)
    result = batch_analyze(
        conversations=conversations,
        schema_name=schema,
        provider=provider or config.default_provider,
        model=config.default_model,
        enable_embeddings=not no_embeddings and config.enable_embeddings,
        sink=sink if to_qdrant else None,
        on_progress=_progress,
    )

    if output_dir:
        _Path(output_dir).mkdir(parents=True, exist_ok=True)
        from analyxa.sinks.json_sink import JsonSink
        for r, conv in zip(result.results, conversations):
            out_path = _Path(output_dir) / f"{conv['id']}.json"
            JsonSink(out_path).write(r.to_flat_dict())

    rate_pct = result.success_rate * 100
    click.echo(
        f"\nBatch complete: {result.successful}/{result.total} successful "
        f"({rate_pct:.1f}%) in {result.elapsed_seconds:.1f}s"
    )
    if output_dir:
        click.echo(f"Results saved to: {output_dir}")


# ------------------------------------------------------------------
# search command
# ------------------------------------------------------------------

@main.command()
@click.argument("query")
@click.option("--limit", "-n", default=5, help="Number of results")
@click.option("--schema", "-s", default=None, help="Filter by schema")
@click.option("--sentiment", default=None, help="Filter by sentiment")
def search(query, limit, schema, sentiment):
    """Search analyzed conversations by semantic similarity."""
    from analyxa.embeddings import EmbeddingGenerator
    from analyxa.sinks.qdrant_sink import QdrantSink

    gen = EmbeddingGenerator()
    embedding = gen.generate(query)
    if embedding is None:
        click.echo("❌ Could not generate query embedding. Check OPENAI_API_KEY.", err=True)
        sys.exit(1)

    filters = {}
    if schema:
        filters["_meta.schema_name"] = schema
    if sentiment:
        filters["sentiment"] = sentiment

    qs = QdrantSink()
    results = qs.search_similar(embedding, limit=limit, filters=filters or None)

    click.echo(f"Results ({len(results)} found):\n")
    for i, r in enumerate(results, 1):
        payload = r["payload"]
        title = payload.get("title", "(no title)")
        schema_name = payload.get("_meta", {}).get("schema_name", "?")
        sent = payload.get("sentiment", "?")
        outcome = payload.get("session_outcome", "?")
        summary = payload.get("summary", "")[:80]
        click.echo(f"{i}. [{r['score']:.2f}] {title}")
        click.echo(f"   Schema: {schema_name} | Sentiment: {sent} | Outcome: {outcome}")
        click.echo(f"   Summary: {summary}...")
        click.echo()


# ------------------------------------------------------------------
# redis group
# ------------------------------------------------------------------

@main.group("redis")
def redis_group():
    """Manage Redis conversation queue."""
    pass


@redis_group.command("push")
@click.argument("file", type=click.Path(exists=True))
@click.option("--schema", "-s", default="universal")
@click.option("--id", "conv_id", default=None)
def redis_push(file, schema, conv_id):
    """Push a conversation file to the Redis queue."""
    from pathlib import Path as _Path
    from analyxa.sources.redis_source import RedisSource

    conversation = _Path(file).read_text(encoding="utf-8")
    rs = RedisSource()
    cid = rs.push(conversation, conversation_id=conv_id, schema=schema)
    click.echo(f"✅ Pushed to Redis: {cid}")


@redis_group.command("list")
@click.option("--status", type=click.Choice(["pending", "analyzed", "failed"]), default=None)
def redis_list(status):
    """List conversations in Redis."""
    from analyxa.sources.redis_source import RedisSource

    rs = RedisSource()
    items = rs.list_all(status=status)

    if not items:
        click.echo("No conversations found.")
        return

    click.echo(f"{'ID':<38}  {'Schema':<12}  {'Status':<10}  {'Pushed At'}")
    click.echo("-" * 85)
    for item in items:
        click.echo(
            f"{item['id']:<38}  {item['schema']:<12}  {item['status']:<10}  {item['pushed_at']}"
        )


@redis_group.command("process")
@click.option("--max", "max_items", default=None, type=int)
@click.option("--provider", "-p", default=None)
@click.option("--no-embeddings", is_flag=True)
def redis_process(max_items, provider, no_embeddings):
    """Process pending conversations from Redis queue."""
    from analyxa.config import get_config
    from analyxa.batch import batch_analyze_from_redis
    from analyxa.sources.redis_source import RedisSource
    from analyxa.sinks.qdrant_sink import QdrantSink

    config = get_config()

    def _progress(current, total, result):
        status = "✅" if result and result.validation_errors == [] else "⚠️" if result else "❌"
        click.echo(f"  [{current}/{total}] {status}", err=True)

    result = batch_analyze_from_redis(
        redis_source=RedisSource(),
        qdrant_sink=QdrantSink(),
        max_items=max_items,
        provider=provider or config.default_provider,
        model=config.default_model,
        enable_embeddings=not no_embeddings and config.enable_embeddings,
        on_progress=_progress,
    )

    rate_pct = result.success_rate * 100
    click.echo(
        f"\nProcessed: {result.successful}/{result.total} successful "
        f"({rate_pct:.1f}%) in {result.elapsed_seconds:.1f}s"
    )


@redis_group.command("flush")
@click.confirmation_option(prompt="Are you sure you want to delete all conversations?")
def redis_flush():
    """Flush all conversations from Redis."""
    from analyxa.sources.redis_source import RedisSource

    rs = RedisSource()
    deleted = rs.flush()
    click.echo(f"✅ Flushed {deleted} keys from Redis.")


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
