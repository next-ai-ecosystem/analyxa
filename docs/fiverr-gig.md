# Fiverr Gig — Analyxa Deployment Service

> Copy listo para publicar en Fiverr. Copiar secciones directamente.

---

## Gig Details

**Title:** I will deploy AI conversation analytics on your server — Analyxa

**Category:** Programming & Tech → AI Services → AI Applications

**Tags SEO:** ai analytics, conversation analytics, chatbot analytics, ai agent analytics, customer support analytics, sentiment analysis, llm analytics, qdrant, redis, ai deployment

---

## Description

### Transform Your AI Conversations Into Actionable Intelligence

Your AI agents handle thousands of conversations daily. But what's actually happening in them? Are customers satisfied? Are issues being resolved? Are there patterns you're missing?

**Analyxa** is a multi-dimensional extraction engine that analyzes every conversation and extracts structured intelligence — sentiment, risk signals, resolution quality, intent, and more — stored as searchable semantic vectors.

### What You Get

I'll deploy Analyxa on your server with:

- Full pipeline: Redis queue → Analyxa engine → Qdrant vector database
- Configured schema matched to your vertical (support, sales, coaching, or custom)
- CLI ready to use: `analyxa analyze`, `analyxa batch`, `analyxa search`
- Docker infrastructure (Redis + Qdrant) running and monitored
- Python API for integration with your existing systems
- Documentation and quickstart guide

### How It Works

1. Conversations enter the pipeline (file, API, or Redis queue)
2. Analyxa extracts N dimensions per conversation using Claude or GPT-4o
3. Results stored as structured JSON + 1,536-dimensional semantic vectors
4. Search by similarity, filter by sentiment, batch process thousands

### Schemas Available

| Schema | Fields | Best For |
|--------|--------|----------|
| Universal | 10 | Any conversation type |
| Support | 16 | Customer service teams |
| Sales | 16 | Sales & prospecting |
| Coaching | 18 | Coaching & therapeutic sessions |
| Custom | You decide | Your specific use case |

### Tech Stack

- Python 3.10+ / Apache 2.0 open source
- LLM: Anthropic Claude Sonnet or OpenAI GPT-4o
- Vector DB: Qdrant (cosine similarity search)
- Queue: Redis 7
- Infrastructure: Docker Compose

### Requirements From You

- VPS or server with SSH access (Ubuntu 22.04+ recommended, 4GB+ RAM)
- API key for Anthropic or OpenAI
- Sample conversations for schema tuning (Professional & Enterprise tiers)

**Response time:** I typically respond within 2 hours and can start deployment the same day.

---

## Tiers

### Tier 1 — Standard Deployment ($297)

- **Delivery:** 3 days
- **Revisions:** 1

What's included:
- Analyxa engine deployed and configured on your server
- Universal schema (10 fields) analyzing any conversation type
- Redis + Qdrant Docker infrastructure
- CLI + Python API ready to use
- Basic documentation and quickstart
- 1 test analysis to verify everything works

### Tier 2 — Vertical Schema Deployment ($497)

- **Delivery:** 5 days
- **Revisions:** 2

What's included:
- Everything in Standard, plus:
- Vertical schema selected and tuned for your industry (support, sales, coaching)
- Schema prompt_hints optimized with your real conversation samples
- Batch processing configured for your volume
- 10 test analyses with quality review
- 30-minute video call walkthrough

### Tier 3 — Custom Schema + Full Integration ($997)

- **Delivery:** 7 days
- **Revisions:** 3

What's included:
- Everything in Professional, plus:
- Custom schema designed specifically for your business (up to 20 fields)
- Production pipeline: your data source → Redis → Analyxa → Qdrant
- API integration with your existing system
- Alerting setup for critical signals (churn risk, escalation, etc.)
- 3 months of email support for schema tuning and troubleshooting
- Priority response time

---

## FAQ

**Q: What LLM provider do I need?**
A: Analyxa works with Anthropic (Claude) or OpenAI (GPT-4o). You'll need an API key from at least one. I recommend Anthropic Claude for best extraction quality.

**Q: How many conversations can it handle?**
A: No hard limit. The Pro plan at 5,000/month costs roughly $25-50 in API calls. Enterprise clients process 50,000+ monthly.

**Q: Can I add my own fields later?**
A: Yes! Analyxa schemas are YAML files. You can add fields by editing the schema — the prompts generate dynamically, no code changes needed.

**Q: Do I need my own server?**
A: Yes, you need a VPS or server with SSH access. I recommend at least 4GB RAM running Ubuntu. I can help you set up a Contabo or DigitalOcean server if needed (separate order).

**Q: Is this open source?**
A: The core engine is Apache 2.0 open source. What you're paying for is the deployment, configuration, schema optimization, and support — not the software itself.

**Q: What if I'm not satisfied?**
A: I offer revisions on every tier. If the deployment doesn't meet the agreed specifications, I'll fix it or refund you.

---

## Gig Images (specs for design)

**Image 1 (thumbnail):**
Dark background with code-style visualization. Title: "AI Conversation Analytics".
Subtitle: "Extract sentiment, risk, intent & more from every conversation."
Analyxa logo/wordmark prominent.

**Image 2 (pipeline diagram):**
Visual flowchart: Conversation → Analyxa → JSON + Vector
Showing: Redis → Engine → Qdrant with sample field values

**Image 3 (schema comparison):**
Table showing 4 schemas side by side with field counts
Universal: 10, Support: 16, Sales: 16, Coaching: 18

**Image 4 (CLI screenshot):**
Real terminal screenshot of `analyxa schemas list` and a sample analysis output
