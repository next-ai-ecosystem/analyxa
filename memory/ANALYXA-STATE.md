# ANALYXA — Estado del Proyecto

> Fuente de verdad del estado actual. Se actualiza al final de cada IF.
> Última actualización: 2026-03-12 — Sesión 0

---

## Estado General

| Dimensión | Valor |
|-----------|-------|
| **Fase actual** | Fase 0 — Inicialización |
| **Bloqueo activo** | Ninguno |
| **Siguiente acción** | Preparar workspace en VPS + diseñar IF-001: Schema System |
| **Días transcurridos** | 0 (inicio: 2026-03-12) |
| **Sesiones completadas** | 0 |

---

## Progreso por Fase

### Fase 0 — Inicialización
- [x] Acta Fundacional generada y validada
- [x] Proyecto Claude creado
- [x] Artefactos MEMORIA inicializados
- [x] Knowledge base cargado
- [ ] VPS/workspace preparado
- [ ] Git inicializado
- [ ] Claude Code verificado

### Fase 1 — Motor Core
- [ ] Schema system (schema.py + universal.yaml + support.yaml)
- [ ] Prompt generator (prompt_builder.py)
- [ ] LLM client (llm_client.py)
- [ ] Analyzer pipeline (analyzer.py + embeddings + sources + sinks)

### Fase 2 — CLI + Integraciones
- [ ] CLI + config (cli.py, config.py)
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

---

## Métricas

| Métrica | Actual | Target |
|---------|--------|--------|
| Tests pasando | 0 | — |
| IFs ejecutadas | 0 | — |
| Schemas implementados | 0 | 4 |
