# ANALYXA — Contexto para Claude

> Este archivo es la puerta de entrada al proyecto.
> Cualquier sesión de Claude que trabaje en este proyecto debe leer este archivo primero.
> Última actualización: 2026-03-12

---

## ¿Qué es Analyxa?

Analyxa es un motor de extracción multi-dimensional que convierte conversaciones de agentes de IA en inteligencia estructurada, indexada y consultable. Toma una conversación opaca y la descompone en N dimensiones configurables (sentimiento, intensidad, temas, riesgo, progreso, etc.) almacenadas como vectores semánticos de 1,536 dimensiones.

**Dominio:** analyxa.ai
**Paquete PyPI:** analyxa
**Licencia:** Apache 2.0 (motor) + Propietario (schemas premium, cloud)
**Origen:** Genericización de MNEMOS, el motor de análisis clínico de Ishara (plataforma terapéutica IA)

---

## Arquitectura

```
Conversación → [Source] → [Analyzer] → [LLM + Schema YAML] → [JSON N campos + Vector 1536D] → [Sink]
```

**Sources:** Redis, archivos, API REST
**Sinks:** Qdrant, JSON, stdout
**LLM:** Claude Sonnet (primario), OpenAI GPT-4o (compatible)
**Embeddings:** OpenAI text-embedding-3-small (1536D)
**Schemas:** YAML configurables. Universal (10 campos) + Verticales premium

---

## Schema Universal (10 campos base)

| # | Campo | Tipo | Descripción |
|---|-------|------|-------------|
| 1 | title | string | Nombre corto de la sesión (5-8 palabras) |
| 2 | summary | string | Resumen 3-5 oraciones. Se vectoriza. |
| 3 | sentiment | keyword | positive / negative / mixed / neutral |
| 4 | sentiment_intensity | keyword | low / medium / high |
| 5 | topics | keyword[] | Temas reales detectados |
| 6 | session_outcome | keyword | resolved / unresolved / escalated / abandoned |
| 7 | user_intent | string | Lo que el usuario realmente buscaba |
| 8 | risk_signals | keyword[] | Señales de alerta |
| 9 | key_entities | keyword[] | Personas, productos, fechas mencionadas |
| 10 | action_items | string[] | Compromisos o siguientes pasos |

---

## Verticales Premium

- **Soporte:** +6 campos (satisfaction_prediction, issue_category, escalation_needed, resolution_quality, first_contact_resolution, customer_effort_score)
- **Ventas:** +6 campos (buying_stage, objections, budget_signals, decision_urgency, competitive_mentions, next_best_action)
- **Coaching:** +8 campos (emotional_valence, emotional_intensity, progress_indicators, behavioral_patterns, growth_markers, therapeutic_momentum, adaptation_level, coping_strategies)

---

## Stack Tecnológico

| Componente | Tecnología |
|-----------|-----------|
| LLM primario | Claude Sonnet (Anthropic) |
| Embeddings | OpenAI text-embedding-3-small |
| Conversaciones | Redis 7 (Docker) |
| Vectores | Qdrant (Docker) |
| Lenguaje | Python 3.10+ |
| CLI | Click |
| VPS | Contabo 66.94.117.83, Ubuntu 22.04, 8GB RAM |

---

## Estructura del Proyecto

```
/opt/analyxa/
├── memory/              # Artefactos MEMORIA v3.0
├── src/analyxa/         # Código fuente
│   ├── analyzer.py      # Orquestador principal
│   ├── schema.py        # Carga y valida schemas YAML
│   ├── prompt_builder.py
│   ├── llm_client.py
│   ├── embeddings.py
│   ├── config.py
│   ├── cli.py
│   ├── batch.py
│   ├── sources/         # redis_source.py, file_source.py
│   ├── sinks/           # qdrant_sink.py, json_sink.py, stdout_sink.py
│   └── schemas/         # universal.yaml, support.yaml, sales.yaml, coaching.yaml
├── tests/
├── examples/
├── docs/
├── docker/
├── .env
└── pyproject.toml
```

---

## Sistema de Memoria

Protocolo MEMORIA v3.0. Los archivos viven en `memory/`:

| Archivo | Propósito | Actualización |
|---------|-----------|---------------|
| CLAUDE.md | Puerta de entrada | Cuando cambian fundamentos |
| ANALYXA-STATE.md | Estado actual | Cada IF completada |
| ANALYXA-BLUEPRINT.md | Plan de fabricación | Cada IF completada |
| ANALYXA-CHANGELOG.md | Log de cambios | Cada IF completada |
| ANALYXA-DECISIONS.md | Decisiones (ADR) | Cada decisión importante |

### Protocolo de sesión

**Al iniciar:** Leer ANALYXA-STATE.md → verificar consistencia (Gate)
**Durante:** Diseñar IF según ANALYXA-BLUEPRINT.md
**Al cerrar:** Verificar que fabricante actualizó memoria

---

## Modelo de Negocio

1. **GitHub Open Source** → Adopción de developers
2. **Product Hunt + Content** → Visibilidad
3. **Fiverr + Servicios directos** → Ingresos inmediatos ($297-$997)
4. **Cloud API SaaS** → Escala ($49-$199/mes)

---

## Estado Actual

> **Ver ANALYXA-STATE.md para el estado detallado actualizado.**
