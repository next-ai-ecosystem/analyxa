# ANALYXA — Estado del Proyecto

> Fuente de verdad del estado actual. Se actualiza al final de cada IF.
> Última actualización: 2026-03-14 — Sesión 9

---

## Estado General

| Dimensión | Valor |
|-----------|-------|
| **Fase actual** | Fase 1.5 — Primeros Ingresos |
| **Bloqueo activo** | PyPI token + API keys (pendientes de Javier) |
| **Siguiente acción** | Javier: configurar accesos. Luego IF-010: publicar + Ishara dogfooding |
| **Días transcurridos** | 3 (inicio: 2026-03-12) |
| **Sesiones completadas** | 9 |

---

## Progreso por Fase

### Fase 0 — Inicialización ✅
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

### Fase 2 — CLI + Integraciones ✅
- [x] CLI + config (cli.py, config.py, pyproject.toml)
- [x] Redis source + Qdrant sink + batch
- [x] Schemas verticales (sales.yaml, coaching.yaml) + 8 conversaciones ejemplo + dogfooding

### Fase 3 — Open Source Launch
- [x] Packaging (README, docs, LICENSE, CONTRIBUTING, build verified)
- [ ] Publicación (GitHub push, PyPI publish) — requiere remote + token

### Fase 1.5 — Primeros Ingresos
- [x] Fiverr gig (copy completo, listo para publicar)
- [x] Landing page analyxa.ai (servida en VPS, http://66.94.117.83/)
- [ ] Primer cliente (Ishara dogfooding)

---

## Dependencias Externas

| Dependencia | Estado | Notas |
|-------------|--------|-------|
| VPS 66.94.117.83 | OK | Contabo, Ubuntu 22.04, 8GB RAM |
| Redis | OK | Docker, v7-alpine, localhost:6379 |
| Qdrant | OK | Docker, latest, localhost:6333 |
| Nginx | OK | Sirviendo landing en puerto 80 |
| Anthropic API | Pendiente | Key placeholder en .env |
| OpenAI API | Pendiente | Key placeholder en .env |
| GitHub remote | OK | next-ai-ecosystem/analyxa |
| PyPI token | Pendiente | Javier debe agregar |
| DNS analyxa.ai | Pendiente | Javier debe apuntar a 66.94.117.83 |

---

## Métricas

| Métrica | Actual | Target |
|---------|--------|--------|
| Tests pasando | 98 | — |
| IFs ejecutadas | 9 | — |
| Schemas implementados | 4 | 4 |
| Landing page | Servida | http://66.94.117.83/ |
| Fiverr gig | Listo | Pendiente publicar |
| PyPI published | pendiente | v0.1.0 |
| GitHub pushed | ✅ | next-ai-ecosystem/analyxa |
