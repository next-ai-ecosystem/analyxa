# ANALYXA — Registro de Decisiones Arquitectónicas

> Cada decisión importante se documenta aquí con contexto completo.
> No se edita retroactivamente. Solo se añaden nuevas entradas.
> Formato ADR (Architecture Decision Record).

---

## ADR-001: Adopción de Protocolo MEMORIA v3.0

**Fecha:** 2026-03-12
**Estado:** Aceptada

**Contexto:** El proyecto requiere desarrollo en múltiples sesiones con agentes IA sin memoria persistente. La metodología fue validada en un proyecto anterior con 9 IFs exitosas en 2 días.

**Decisión:** Adoptar Protocolo MEMORIA v3.0 con flujo dual (arquitecto en Claude Proyecto + fabricante en Claude Code), 5 artefactos de memoria, e instrucciones de fabricación como unidad atómica de trabajo.

**Consecuencias:**
- (+) Continuidad garantizada entre sesiones
- (+) Separación de responsabilidades (diseño vs ejecución)
- (+) Historial completo de decisiones y cambios
- (-) Overhead de transporte manual entre agentes

---

## ADR-002: Extracción estructurada, no memory layer

**Fecha:** 2026-03-12
**Estado:** Aceptada

**Contexto:** El mercado de herramientas para conversaciones IA tiene memory layers (Mem0, Zep, Letta) pero nadie ofrece extracción multi-dimensional configurable.

**Decisión:** Posicionar Analyxa como motor de extracción estructurada que complementa (no compite con) memory layers.

**Consecuencias:**
- (+) Gap de mercado claro — nadie lo hace
- (+) Compatible con todos los memory layers existentes
- (-) Categoría nueva requiere educación del mercado

---

## ADR-003: Open source motor + propietario schemas/cloud

**Fecha:** 2026-03-12
**Estado:** Aceptada

**Contexto:** Necesitamos distribución masiva (open source) + monetización (propietario). Patrón validado por Mem0, Zep, Letta.

**Decisión:** Motor de análisis y schema universal gratuitos (Apache 2.0). Schemas verticales premium, prompts optimizados, análisis longitudinal, alertas y cloud API como productos pagados.

**Consecuencias:**
- (+) Adopción de developers sin fricción
- (+) Moat claro entre gratuito y pagado
- (-) Requiere que el motor gratuito sea suficientemente bueno para generar demanda

---

## ADR-004: Nombre Analyxa (analyxa.ai)

**Fecha:** 2026-03-12
**Estado:** Aceptada

**Contexto:** Rebranding del proyecto originalmente llamado TESSERA. Se necesita nombre evocativo, con dominio .ai disponible y namespace limpio en GitHub/PyPI.

**Decisión:** Analyxa — combinación de "analysis" + sufijo tech. Dominio analyxa.ai registrado. GitHub: next-ai-ecosystem/analyxa. PyPI: analyxa.

**Consecuencias:**
- (+) Nombre evocativo y memorable
- (+) Dominio .ai premium
- (+) Namespace limpio en todas las plataformas
- (+) Bajo la org corporativa next-ai-ecosystem

---

## ADR-005: Código 100% nuevo, no reciclado

**Fecha:** 2026-03-12
**Estado:** Aceptada

**Contexto:** Existía código funcional del proyecto anterior (TESSERA). Se debatió entre reciclar o reescribir.

**Decisión:** Escribir todo el código desde cero. El diseño del negocio se transporta fielmente, el código no.

**Consecuencias:**
- (+) Naming consistente (analyxa en todo el código)
- (+) Oportunidad de mejorar con lecciones aprendidas
- (+) Sin deuda técnica heredada
- (-) Más tiempo de desarrollo (mitigado por IFs ya validadas)

---

## ADR-006: VPS compartido con TESSERA (66.94.117.83)

**Fecha:** 2026-03-12
**Estado:** Aceptada

**Contexto:** El VPS de Contabo ya tiene Docker, Redis, Qdrant instalados. Crear otro VPS tiene costo adicional.

**Decisión:** Usar el mismo VPS pero workspace separado (/opt/analyxa vs /opt/tessera). Sin compartir código, credenciales, ni bases de datos.

**Consecuencias:**
- (+) Ahorro de costos (~$10/mes)
- (+) Infraestructura Docker ya operativa
- (-) Riesgo de contaminación si no se mantienen separados
- Mitigación: workspaces completamente independientes, .env separados

---

## ADR-007: GitHub org next-ai-ecosystem

**Fecha:** 2026-03-12
**Estado:** Aceptada

**Contexto:** Ya existe la cuenta GitHub next-ai-ecosystem. Se debatió entre org dedicada (analyxa) o org corporativa.

**Decisión:** Usar next-ai-ecosystem como org. El repo es next-ai-ecosystem/analyxa. Esto posiciona a Analyxa como producto de Next AI Ecosystem, junto a futuros productos.

**Consecuencias:**
- (+) Profesional y corporativo
- (+) Multi-producto bajo una marca
- (-) El nombre del repo no es el mismo que la org

---

## ADR-008: Speed gate 30 días para primer ingreso

**Fecha:** 2026-03-12
**Estado:** Aceptada

**Contexto:** Riesgo de construir durante meses sin validar con dinero real. El patrón de "build first, monetize later" mata startups.

**Decisión:** El proyecto debe generar su primer ingreso real antes del día 30. Canal: Fiverr + servicios directos ($297-$997).

**Consecuencias:**
- (+) Disciplina financiera desde día 1
- (+) Validación de mercado temprana
- (-) Puede forzar un MVP menos pulido

---

## ADR-009: Ishara como primer cliente (dogfooding)

**Fecha:** 2026-03-12
**Estado:** Aceptada

**Contexto:** Ishara usa MNEMOS internamente para análisis clínico de sesiones terapéuticas. Analyxa puede reemplazar ese módulo con el schema coaching.

**Decisión:** Ishara será el primer "cliente" de Analyxa. El schema coaching con 18 campos replicará las dimensiones clínicas de MNEMOS.

**Consecuencias:**
- (+) Caso de estudio real para marketing
- (+) Dogfooding con datos de producción
- (+) "Analyxa powers clinical analysis for a therapeutic AI platform"

---
