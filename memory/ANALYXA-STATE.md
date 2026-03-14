# ANALYXA — Estado del Proyecto

> Fuente de verdad del estado actual. Se actualiza al final de cada IF.
> Última actualización: 2026-03-14 — Sesión 5

---

## Estado General

| Dimensión | Valor |
|-----------|-------|
| **Fase actual** | Fase 2 — CLI + Integraciones |
| **Bloqueo activo** | Ninguno |
| **Siguiente acción** | IF-006: Redis + Qdrant + Batch (Paso 2.2) |
| **Días transcurridos** | 2 (inicio: 2026-03-12) |
| **Sesiones completadas** | 5 |

---

## Progreso por Fase

### Fase 0 — Inicialización
- [x] Acta Fundacional generada y validada
- [x] Proyecto Claude creado
- [x] Artefactos MEMORIA inicializados
- [x] Knowledge base cargado
- [x] VPS/workspace preparado
- [x] Git inicializado

### Fase 1 — Motor Core ✅
- [x] Schema system (schema.py + universal.yaml + support.yaml)
- [x] Prompt generator (prompt_builder.py)
- [x] LLM client (llm_client.py)
- [x] Analyzer pipeline (analyzer.py + embeddings + sources + sinks)

### Fase 2 — CLI + Integraciones
- [x] CLI + config (cli.py, config.py, pyproject.toml)
- [ ] Redis source + Qdrant sink + batch
- [ ] Schemas verticales (sales, coaching) + dogfooding

### Fase 3 — Open Source Launch
- [ ] Packaging (README, pyproject.toml, docs, LICENSE)
- [ ] Publicación (GitHub push, PyPI publish)

### Fase 1.5 — Primeros Ingresos
- [ ] Fiverr gig
- [ ] Landing page analyxa.ai
- [ ] Primer cliente (Ishara dogfooding)

---

## Dependencias Externas

| Dependencia | Estado | Notas |
|-------------|--------|-------|
| VPS 66.94.117.83 | OK | Contabo, Ubuntu 22.04, 8GB RAM |
| Redis | Pendiente | Docker container por instalar |
| Qdrant | Pendiente | Docker container por instalar |
| Anthropic API | Pendiente | Key por configurar en .env |
| OpenAI API | Pendiente | Key por configurar en .env |
| anthropic SDK | OK | v0.84.0 instalado |
| openai SDK | OK | v2.26.0 instalado |
| click | OK | v8.x instalado |
| python-dotenv | OK | v1.x instalado |

---

## Métricas

| Métrica | Actual | Target |
|---------|--------|--------|
| Tests pasando | 64 | — |
| IFs ejecutadas | 5 | — |
| Schemas implementados | 2 | 4 |
