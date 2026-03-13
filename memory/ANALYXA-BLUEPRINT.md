# ANALYXA — Blueprint de Fabricación

> Pipeline de fabricación vivo. Se actualiza conforme se completan pasos.
> Última actualización: 2026-03-12

---

## Resumen del Pipeline

| Fase | Descripción | Estimado | Estado |
|------|-------------|----------|--------|
| Fase 0: Inicialización | Setup proyecto y servidor | 1 sesión | 🔄 En progreso |
| Fase 1: Motor Core | Schema, prompt, LLM, analyzer | Días 1-14 | Pendiente |
| Fase 2: CLI + Integraciones | CLI, Redis, Qdrant, batch, schemas | Días 8-20 | Pendiente |
| Fase 3: Open Source Launch | README, PyPI, GitHub, docs | Días 15-25 | Pendiente |
| Fase 1.5: Primeros Ingresos | Fiverr, landing, primer cliente | Días 20-30 | Pendiente |
| Fase 4: Visibilidad + Escala | Product Hunt, blog, SaaS | Días 30-90 | Pendiente |

**Speed gate:** Primer ingreso real antes del día 30.

---

## Fase 0 — Inicialización

- [x] Acta Fundacional generada y validada
- [x] Proyecto Claude creado con system prompt MEMORIA v3.0
- [x] 5 artefactos de memoria creados
- [x] Knowledge base cargado
- [ ] VPS: workspace /opt/analyxa creado
- [ ] VPS: Python venv + Git inicializado
- [ ] VPS: Docker (Redis + Qdrant) verificado
- [ ] VPS: Claude Code funcional
- [ ] VPS: .env con API keys configuradas

---

## Fase 1 — Motor Core

### Paso 1.1 — Schema System
- [ ] Diseñar formato YAML del schema (4 secciones: metadata, fields, auto_fields, prompt)
- [ ] Implementar schema.py (SchemaManager, herencia, validación, cache)
- [ ] Crear schemas/universal.yaml (10 campos + 7 auto-campos)
- [ ] Crear schemas/support.yaml (hereda universal + 6 campos)
- [ ] Tests de carga, herencia, validación

### Paso 1.2 — Prompt Generator
- [ ] Implementar prompt_builder.py
- [ ] build_prompt(schema, conversation, context) → {system, user}
- [ ] Tests de prompt_builder

### Paso 1.3 — LLM Client
- [ ] Implementar llm_client.py (Anthropic + OpenAI)
- [ ] LLMResponse dataclass, parser JSON robusto
- [ ] Tests unitarios + integración

### Paso 1.4 — Analyzer Pipeline
- [ ] Implementar analyzer.py (orquestador completo)
- [ ] Implementar embeddings.py (vectores 1536D)
- [ ] Implementar sources/file_source.py
- [ ] Implementar sinks/json_sink.py + stdout_sink.py
- [ ] `from analyxa import analyze` funcional
- [ ] Tests end-to-end

---

## Fase 2 — CLI + Integraciones

### Paso 2.1 — CLI + Config
- [ ] Implementar config.py (centralizado, .env)
- [ ] Implementar cli.py (analyze, schemas list/show)
- [ ] Entry point en pyproject.toml
- [ ] Tests de CLI

### Paso 2.2 — Redis + Qdrant + Batch
- [ ] Implementar redis_source.py
- [ ] Implementar qdrant_sink.py
- [ ] Implementar batch.py
- [ ] CLI: batch, search, redis
- [ ] Tests de infraestructura

### Paso 2.3 — Schemas verticales + Dogfooding
- [ ] Crear sales.yaml (10 + 6 campos)
- [ ] Crear coaching.yaml (10 + 8 campos)
- [ ] 8 conversaciones de ejemplo
- [ ] Script dogfood.py (14 análisis)
- [ ] Tests multi-vertical

---

## Fase 3 — Open Source Launch

### Paso 3.1 — Packaging
- [ ] README.md profesional
- [ ] pyproject.toml final para PyPI
- [ ] docker-compose.yaml
- [ ] LICENSE, CONTRIBUTING.md
- [ ] docs/ (quickstart, schemas, api-reference)
- [ ] Build test verificado

### Paso 3.2 — Publicación
- [ ] GitHub push (next-ai-ecosystem/analyxa)
- [ ] PyPI publish (analyxa v0.1.0)
- [ ] GitHub Release + tag
- [ ] Verificación pip install

---

## Fase 1.5 — Primeros Ingresos

### Paso 1.5.1 — Fiverr
- [ ] Crear gig con 3 tiers ($297/$497/$997)
- [ ] Descripción, FAQ, imágenes

### Paso 1.5.2 — Landing page
- [ ] analyxa.ai con hero, features, pricing, quickstart

### Paso 1.5.3 — Primer cliente
- [ ] Ishara dogfooding (schema coaching 18 campos)
- [ ] Caso de estudio documentado

---

## Principios de Ejecución

1. **Velocidad > Perfección.** Un producto funcional hoy vale más que uno perfecto mañana.
2. **Dinero > Métricas vanidad.** Un cliente pagando vale más que mil seguidores.
3. **Producción > Teoría.** Cada decisión se valida con datos reales.
4. **Documentar = Sobrevivir.** Sin memoria persistente, el proyecto muere entre sesiones.
