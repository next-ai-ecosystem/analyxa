# ANALYXA — Changelog

> Log cronológico de cambios ejecutados.
> Cada entrada: fecha, sesión, ejecutor, qué se hizo, archivos afectados.

---

## 2026-03-12 — Sesión 0: Inicialización

**Tipo:** Inicialización
**Ejecutor:** Javier / Claude Proyecto

### Cambios ejecutados
1. **Acta Fundacional generada y validada**
   - Negocio completo definido: producto, arquitectura, schemas, modelo de negocio, blueprint
   - Identidad: analyxa.ai, GitHub next-ai-ecosystem/analyxa, PyPI analyxa
   - Derivado del diseño estratégico de TESSERA, reconstruido desde cero

2. **Proyecto ANALYXA creado en claude.ai**
   - System prompt MEMORIA v3.0 configurado
   - 5 artefactos de memoria inicializados

3. **Knowledge base cargado**
   - 5 artefactos + Acta Fundacional + Protocolo MEMORIA v3.0

### Archivos generados
- `CLAUDE.md`
- `ANALYXA-STATE.md`
- `ANALYXA-BLUEPRINT.md`
- `ANALYXA-CHANGELOG.md`
- `ANALYXA-DECISIONS.md`

### Siguiente acción
- Preparar workspace en VPS (/opt/analyxa)
- Diseñar IF-001: Schema System

---

## 2026-03-13 — Sesión 1: IF-001 Schema System

**Tipo:** Fabricación
**IF:** IF-001
**Ejecutor:** Claude Code
**Paso Blueprint:** Fase 1, Paso 1.1

### Cambios ejecutados
1. **Workspace VPS preparado**
   - /opt/analyxa estructura completa verificada
   - Python venv, Git, .gitignore confirmados operativos

2. **Schema System implementado**
   - schema.py: SchemaManager con carga, herencia, validación, cache
   - universal.yaml: 10 campos base + 7 auto-campos + prompt guidelines
   - support.yaml: hereda universal + 6 campos soporte (16 total)

3. **Tests completos**
   - 10 tests cubriendo: carga, herencia, cache, listado, validación, errores
   - Todos pasando (10/10)

### Archivos creados
- src/analyxa/__init__.py
- src/analyxa/schema.py
- src/analyxa/schemas/universal.yaml
- src/analyxa/schemas/support.yaml
- tests/test_schema.py

### Git
- commit: `feat(IF-001): schema system — SchemaManager + universal/support schemas + 10 tests`

### Siguiente acción
- IF-002: Prompt Generator (prompt_builder.py)

---

## 2026-03-13 — Sesión 2: IF-002 Prompt Generator

**Tipo:** Fabricación
**IF:** IF-002
**Ejecutor:** Claude Code
**Paso Blueprint:** Fase 1, Paso 1.2

### Cambios ejecutados
1. **Prompt Generator implementado**
   - prompt_builder.py: build_prompt() genera prompts dinámicos desde schema YAML
   - Generación de field definitions, JSON template, context injection
   - Soporte para idioma configurable en respuestas de texto libre

2. **Tests completos**
   - 12 tests cubriendo: estructura, campos, template JSON, contexto, idioma, herencia support
   - Todos pasando (22 total acumulados)

### Archivos creados
- src/analyxa/prompt_builder.py
- tests/test_prompt_builder.py

### Git
- commit: `feat(IF-002): prompt generator — dynamic prompt building from YAML schemas + 12 tests`

### Siguiente acción
- IF-003: LLM Client (llm_client.py)

---

## 2026-03-14 — Sesión 3: IF-003 LLM Client

**Tipo:** Fabricación
**IF:** IF-003
**Ejecutor:** Claude Code
**Paso Blueprint:** Fase 1, Paso 1.3

### Cambios ejecutados
1. **LLM Client implementado**
   - llm_client.py: LLMClient multi-provider (Anthropic + OpenAI)
   - LLMResponse dataclass con metadata completa
   - Parser JSON robusto (directo, code fences, text mixto)
   - Imports condicionales — no falla si un SDK no está instalado
   - Manejo de errores graceful — nunca lanza excepciones al caller

2. **Tests completos (mocks, no requieren API keys)**
   - 14 tests cubriendo: dataclass, parser JSON (5 casos), init providers, analyze mock Anthropic/OpenAI, errores API, respuesta no-JSON
   - Todos pasando (36 total acumulados)

### Archivos creados
- src/analyxa/llm_client.py
- tests/test_llm_client.py

### Dependencias agregadas
- anthropic v0.84.0
- openai v2.26.0

### Git
- commit: `feat(IF-003): LLM client — multi-provider (Anthropic/OpenAI) + robust JSON parser + 14 tests`

### Siguiente acción
- IF-004: Analyzer Pipeline (analyzer.py + embeddings + sources + sinks)

---

## 2026-03-14 — Sesión 4: IF-004 Analyzer Pipeline

**Tipo:** Fabricación
**IF:** IF-004
**Ejecutor:** Claude Code
**Paso Blueprint:** Fase 1, Paso 1.4

### Cambios ejecutados
1. **Analyzer Pipeline completo**
   - analyzer.py: Analyzer + AnalysisResult dataclass + analyze() convenience function
   - Pipeline: schema → prompt → LLM → validate → embed → result
   - `from analyxa import analyze` funcional

2. **Embeddings** — embeddings.py: EmbeddingGenerator degradación silenciosa

3. **Sources** — sources/file_source.py: read(), read_messages(), metadata()

4. **Sinks** — json_sink.py + stdout_sink.py

5. **14 tests end-to-end con mocks** — 50 total acumulados

### Archivos creados/modificados
- src/analyxa/analyzer.py, embeddings.py, __init__.py (actualizado)
- src/analyxa/sources/__init__.py, file_source.py
- src/analyxa/sinks/__init__.py, json_sink.py, stdout_sink.py
- tests/test_analyzer.py

### Git
- commit: `feat(IF-004): analyzer pipeline — full extraction engine + embeddings + sources/sinks + 14 tests`

### HITO: Fase 1 — Motor Core COMPLETA

### Siguiente acción
- IF-005: CLI + Config (Fase 2, Paso 2.1)

---
## 2026-03-14 — Sesión 5: IF-005 CLI + Config

**Tipo:** Fabricación
**IF:** IF-005
**Ejecutor:** Claude Code
**Paso Blueprint:** Fase 2, Paso 2.1

### Cambios ejecutados
1. **Config centralizado**
   - config.py: AnalyxaConfig con 12 settings (.env + defaults + singleton)
   - Refactor llm_client.py y embeddings.py para usar config (backwards compatible)

2. **CLI completo con Click**
   - cli.py: 4 comandos (analyze, schemas list, schemas show, version)
   - analyze: --schema, --output, --format, --provider, --model, --no-embeddings, --context
   - schemas list: muestra todos los schemas con metadata
   - schemas show: detalle de campos por schema

3. **pyproject.toml**
   - Packaging PEP 621 completo
   - Entry point: analyxa → cli:main
   - Package data: schemas/*.yaml incluidos
   - pip install -e . funcional

4. **Tests**
   - 6 tests config + 8 tests CLI = 14 nuevos (64 total)

### Archivos creados/modificados
- src/analyxa/config.py (nuevo)
- src/analyxa/cli.py (nuevo)
- pyproject.toml (nuevo)
- src/analyxa/llm_client.py (refactor: config support)
- src/analyxa/embeddings.py (refactor: config support)
- tests/test_config.py (nuevo)
- tests/test_cli.py (nuevo)

### Dependencias agregadas
- click
- python-dotenv

### Git
- commit: `feat(IF-005): CLI + config — Click CLI + centralized config + pyproject.toml + 14 tests`

### Siguiente acción
- IF-006: Redis + Qdrant + Batch (Paso 2.2)

---
## 2026-03-14 — Sesión 6: IF-006 Redis + Qdrant + Batch

**Tipo:** Fabricación
**IF:** IF-006
**Ejecutor:** Claude Code
**Paso Blueprint:** Fase 2, Paso 2.2

### Cambios ejecutados
1. **Docker Compose** — Redis 7 + Qdrant levantados en docker/docker-compose.yaml
2. **RedisSource** — push, get, pending, next, mark_analyzed/failed, list_all, flush
3. **QdrantSink** — store, search_similar (query_points API), get, count, auto-create collection 1536D cosine; zero vector fallback para puntos sin embedding
4. **BatchProcessor** — batch_analyze (un Analyzer reusado) + batch_analyze_from_redis (cola Redis → Qdrant)
5. **CLI extendido** — 3 comandos nuevos: batch, search, redis (push/list/process/flush)
6. **pyproject.toml** — dependencias redis>=5.0.0, qdrant-client>=1.7.0 agregadas
7. **22 tests nuevos** — 9 redis (integración) + 8 qdrant (integración) + 5 batch (unit mock) → 86 total

### Archivos creados/modificados
- docker/docker-compose.yaml (nuevo)
- src/analyxa/sources/redis_source.py (nuevo)
- src/analyxa/sinks/qdrant_sink.py (nuevo)
- src/analyxa/batch.py (nuevo)
- src/analyxa/cli.py (extendido: batch, search, redis group)
- pyproject.toml (redis + qdrant-client deps)
- tests/test_redis_source.py, test_qdrant_sink.py, test_batch.py (nuevos)

### Fix notable
- qdrant-client v1.17.1 eliminó client.search() → usar client.query_points() con response.points

### Dependencias agregadas
- redis>=5.0.0 (v5.x instalado)
- qdrant-client>=1.7.0 (v1.17.1 instalado)

### Git
- commit: feat(IF-006): Redis + Qdrant + batch — infrastructure layer + 22 tests

### Siguiente acción
- IF-007: Schemas verticales + Dogfooding (Paso 2.3)

---
## 2026-03-14 — Sesión 7: IF-007 Schemas Verticales + Dogfooding

**Tipo:** Fabricación
**IF:** IF-007
**Ejecutor:** Claude Code
**Paso Blueprint:** Fase 2, Paso 2.3

### Cambios ejecutados
1. **Schemas verticales completos**
   - sales.yaml: hereda universal + 6 campos (buying_stage, objections, budget_signals, decision_urgency, competitive_mentions, next_best_action) = 16 total
   - coaching.yaml: hereda universal + 8 campos (emotional_valence, emotional_intensity, progress_indicators, behavioral_patterns, growth_markers, therapeutic_momentum, adaptation_level, coping_strategies) = 18 total

2. **8 conversaciones de ejemplo**
   - universal_greeting.txt, universal_technical.txt
   - support_billing.txt, support_cancellation.txt
   - sales_demo.txt, sales_objection.txt
   - coaching_progress.txt, coaching_crisis.txt

3. **Script dogfood.py**
   - 14 análisis: 8 directos + 6 cross-schema (conv + universal)
   - Quality checks por schema
   - Manejo graceful si API key no está configurada
   - Reporte JSON en examples/results/

4. **Tests multi-vertical (12 tests)**
   - Carga de 4 schemas, field counts, herencia
   - Campos específicos sales y coaching
   - Prompt builder multi-vertical
   - CLI schemas list/show

### Archivos creados
- src/analyxa/schemas/sales.yaml
- src/analyxa/schemas/coaching.yaml
- examples/conversations/ (8 archivos)
- scripts/dogfood.py
- tests/test_multi_vertical.py
- examples/results/ (directorio)

### Tests
- 101 tests pasando (86 previos + 15 nuevos)

### Git
- commit: feat(IF-007): sales + coaching schemas + 8 examples + dogfooding + 12 tests

### HITO: Fase 2 — CLI + Integraciones COMPLETA

### Siguiente acción
- IF-008: Fase 3 — Open Source Launch (README, PyPI, docs, LICENSE)

---
## 2026-03-14 — Sesión 8: IF-008 Open Source Launch

**Tipo:** Fabricación + Publicación
**IF:** IF-008
**Ejecutor:** Claude Code
**Paso Blueprint:** Fase 3, Pasos 3.1 + 3.2

### Cambios ejecutados
1. **README.md** — Profesional con quick start, CLI, Python API, schemas, pipeline, config
2. **LICENSE** — Apache 2.0 completa
3. **CONTRIBUTING.md** — Guía para contributors
4. **docs/** — quickstart.md, schemas.md, api-reference.md
5. **Build test** — wheel verificado, schemas incluidos, install limpio en venv aislado

### Archivos creados
- README.md
- LICENSE
- CONTRIBUTING.md
- docs/quickstart.md
- docs/schemas.md
- docs/api-reference.md

### Build verificado
- `analyxa-0.1.0-py3-none-any.whl` — 4 schemas YAML incluidos
- Install limpio en `/tmp/analyxa-test-install` — `analyxa version` + `analyxa schemas list` OK
- 98 tests pasando

### Publicación pendiente
- GitHub remote no configurado — Javier debe agregar `git remote add origin`
- PyPI token no disponible — Javier debe configurar `.pypirc` o `TWINE_PASSWORD`
- Wheel y sdist listos en `dist/` para publicación inmediata

### Git
- commit: `feat(IF-008): open source packaging — README, docs, LICENSE, build verified`
- tag: v0.1.0

### HITO: Fase 3 — Open Source Launch PARCIAL (packaging listo, publicación pendiente)

### Siguiente acción
- Completar publicación (GitHub push + PyPI publish) cuando Javier configure accesos
- IF-009: Fiverr Gig + Landing Page (Fase 1.5)

---
## 2026-03-14 — Sesión 9: IF-009 Fiverr Gig + Landing Page

**Tipo:** Fabricación (comercial)
**IF:** IF-009
**Ejecutor:** Claude Code
**Paso Blueprint:** Fase 1.5, Pasos 1.5.1 + 1.5.2

### Cambios ejecutados
1. **Fiverr gig completo**
   - docs/fiverr-gig.md: título, descripción, 3 tiers ($297/$497/$997), FAQ, specs de imágenes
   - Listo para copiar a Fiverr

2. **Landing page analyxa.ai**
   - /var/www/analyxa/index.html: single-page, dark theme, responsive
   - Secciones: hero, problem, pipeline, schemas, code examples, pricing, tech stack, footer
   - Nginx configurado y sirviendo en http://66.94.117.83/
   - Terminal estilizada en hero con análisis ejemplo
   - Tabs interactivos para code examples (Python/CLI/Pipeline)

### Archivos creados
- docs/fiverr-gig.md
- /var/www/analyxa/index.html
- /etc/nginx/sites-available/analyxa

### Git
- commit: feat(IF-009): Fiverr gig copy + analyxa.ai landing page + nginx config

### Post-sesión: GitHub push confirmado
- Javier completó GitHub push exitosamente a next-ai-ecosystem/analyxa
- Tag v0.1.0 publicado en GitHub

### Siguiente acción
- Javier: publicar gig en Fiverr, configurar DNS analyxa.ai, PyPI token, API keys
- IF-010: completar publicación PyPI + Ishara dogfooding

---
## 2026-03-14 — Sesión 9 (continuación): PyPI + Dogfooding

**Tipo:** Publicación + Validación

### Cambios ejecutados
1. **API keys configuradas** — Anthropic + OpenAI en .env, verificadas con analyxa version
2. **PyPI v0.1.0 publicado** — https://pypi.org/project/analyxa/0.1.0/
   - Wheel + sdist subidos con twine
   - `pip install analyxa==0.1.0` verificado en VPS
3. **dogfood.py fix** — Corregido para usar get_config() en vez de verificación directa de .env
4. **Dogfooding REAL ejecutado** — 14/14 análisis passed (100%)
   - 0 quality issues en 4 schemas
   - Resultados en examples/results/dogfood_report.json

### HITO: Fase 3 — Open Source Launch COMPLETA
GitHub ✅ + PyPI ✅ + dogfooding validado ✅

### Pendientes de Javier (no bloquean fabricación)
- DNS analyxa.ai → 66.94.117.83
- Certbot HTTPS
- Publicar gig en Fiverr
