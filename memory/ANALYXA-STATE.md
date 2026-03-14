# ANALYXA — Estado del Proyecto

> Fuente de verdad del estado actual. Se actualiza al final de cada IF.
> Última actualización: 2026-03-14 — Sesión 7

---

## Estado General

| Dimensión | Valor |
|-----------|-------|
| **Fase actual** | Fase 2 — CLI + Integraciones ✅ COMPLETA |
| **Bloqueo activo** | Ninguno |
| **Siguiente acción** | IF-008: Fase 3 — Open Source Launch (README, PyPI, docs) |
| **Días transcurridos** | 3 (inicio: 2026-03-12) |
| **Sesiones completadas** | 7 |

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

### Fase 2 — CLI + Integraciones ✅
- [x] CLI + config (cli.py, config.py, pyproject.toml)
- [x] Redis source + Qdrant sink + batch
- [x] Schemas verticales (sales.yaml, coaching.yaml) + 8 conversaciones ejemplo + dogfooding

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
| Redis | OK | Docker, v7-alpine, localhost:6379 |
| Qdrant | OK | Docker, latest, localhost:6333 |
| Anthropic API | Pendiente | Key placeholder en .env — configurar para dogfooding real |
| OpenAI API | Pendiente | Key placeholder en .env — configurar para embeddings |
| anthropic SDK | OK | v0.84.0 instalado |
| openai SDK | OK | v2.26.0 instalado |
| click | OK | v8.x instalado |
| python-dotenv | OK | v1.x instalado |
| redis SDK | OK | v5.x instalado |
| qdrant-client SDK | OK | v1.17.1 instalado |

---

## Métricas

| Métrica | Actual | Target |
|---------|--------|--------|
| Tests pasando | 98 | — |
| IFs ejecutadas | 7 | — |
| Schemas implementados | 4 | 4 |
| Conversaciones ejemplo | 8 | 8 |
