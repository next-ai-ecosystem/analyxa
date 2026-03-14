# ANALYXA — Blueprint de Fabricación

> Pipeline de fabricación vivo. Se actualiza conforme se completan pasos.
> Última actualización: 2026-03-12

---

## Resumen del Pipeline

| Fase | Descripción | Estimado | Estado |
|------|-------------|----------|--------|
| Fase 0: Inicialización | Setup proyecto y servidor | 1 sesión | ✅ Completa |
| Fase 1: Motor Core | Schema, prompt, LLM, analyzer | Días 1-14 | ✅ Completa |
| Fase 2: CLI + Integraciones | CLI, Redis, Qdrant, batch, schemas | Días 8-20 | ✅ Completa |
| Fase 3: Open Source Launch | README, PyPI, GitHub, docs | Días 15-25 | ✅ Completa |
| Fase 1.5: Primeros Ingresos | Fiverr, landing, primer cliente | Días 20-30 | En progreso |
| Fase 4: Visibilidad + Escala | Product Hunt, blog, SaaS | Días 30-90 | Pendiente |

**Speed gate:** Primer ingreso real antes del día 30.

---

## Fase 0 — Inicialización

- [x] Acta Fundacional generada y validada
- [x] Proyecto Claude creado con system prompt MEMORIA v3.0
- [x] 5 artefactos de memoria creados
- [x] Knowledge base cargado
- [x] VPS: workspace /opt/analyxa creado
- [x] VPS: Python venv + Git inicializado
- [ ] VPS: Docker (Redis + Qdrant) verificado
- [ ] VPS: Claude Code funcional
- [ ] VPS: .env con API keys configuradas

---

## Fase 1 — Motor Core

### Paso 1.1 — Schema System
- [x] Diseñar formato YAML del schema (4 secciones: metadata, fields, auto_fields, prompt)
- [x] Implementar schema.py (SchemaManager, herencia, validación, cache)
- [x] Crear schemas/universal.yaml (10 campos + 7 auto-campos)
- [x] Crear schemas/support.yaml (hereda universal + 6 campos)
- [x] Tests de carga, herencia, validación

### Paso 1.2 — Prompt Generator
- [x] Implementar prompt_builder.py
- [x] build_prompt(schema, conversation, context) → {system, user}
- [x] Tests de prompt_builder

### Paso 1.3 — LLM Client
- [x] Implementar llm_client.py (Anthropic + OpenAI)
- [x] LLMResponse dataclass, parser JSON robusto
- [x] Tests unitarios + integración

### Paso 1.4 — Analyzer Pipeline
- [x] Implementar analyzer.py (orquestador completo)
- [x] Implementar embeddings.py (vectores 1536D)
- [x] Implementar sources/file_source.py
- [x] Implementar sinks/json_sink.py + stdout_sink.py
- [x] `from analyxa import analyze` funcional
- [x] Tests end-to-end

---

## Fase 2 — CLI + Integraciones

### Paso 2.1 — CLI + Config
- [x] Implementar config.py (centralizado, .env)
- [x] Implementar cli.py (analyze, schemas list/show)
- [x] Entry point en pyproject.toml
- [x] Tests de CLI

### Paso 2.2 — Redis + Qdrant + Batch
- [x] Implementar redis_source.py
- [x] Implementar qdrant_sink.py
- [x] Implementar batch.py
- [x] CLI: batch, search, redis
- [x] Tests de infraestructura

### Paso 2.3 — Schemas verticales + Dogfooding
- [x] Crear sales.yaml (10 + 6 campos = 16 total)
- [x] Crear coaching.yaml (10 + 8 campos = 18 total)
- [x] 8 conversaciones de ejemplo
- [x] Script dogfood.py (14 análisis, requiere API key real)
- [x] Tests multi-vertical (12 tests)

---

## Fase 3 — Open Source Launch

### Paso 3.1 — Packaging
- [x] README.md profesional
- [x] pyproject.toml final para PyPI
- [x] docker-compose.yaml
- [x] LICENSE, CONTRIBUTING.md
- [x] docs/ (quickstart, schemas, api-reference)
- [x] Build test verificado

### Paso 3.2 — Publicación
- [x] GitHub push (next-ai-ecosystem/analyxa)
- [x] PyPI publish (analyxa v0.1.0)
- [x] GitHub Release + tag
- [x] Verificación pip install

---

## Fase 1.5 — Primeros Ingresos

### Paso 1.5.1 — Fiverr
- [x] Crear gig con 3 tiers ($295/$495/$995)
- [x] Descripción, FAQ, imágenes

### Paso 1.5.2 — Landing page
- [x] analyxa.ai con hero, features, pricing, quickstart
- [x] DNS configurado y propagado
- [x] HTTPS con Let's Encrypt

### Paso 1.5.3 — Primer cliente
- [ ] Ishara dogfooding (schema coaching 18 campos)
- [ ] Caso de estudio documentado

---

## Principios de Ejecución

1. **Velocidad > Perfección.** Un producto funcional hoy vale más que uno perfecto mañana.
2. **Dinero > Métricas vanidad.** Un cliente pagando vale más que mil seguidores.
3. **Producción > Teoría.** Cada decisión se valida con datos reales.
4. **Documentar = Sobrevivir.** Sin memoria persistente, el proyecto muere entre sesiones.
