# Schema Reference

## How Schemas Work

Analyxa uses YAML schemas to define what dimensions to extract from conversations. Schemas are hierarchical: vertical schemas inherit all fields from `universal` and add domain-specific ones.

```
universal (10 fields)
├── support (10 + 6 = 16 fields)
├── sales (10 + 6 = 16 fields)
└── coaching (10 + 8 = 18 fields)
```

## Universal Schema (10 fields)

The base schema included in every analysis.

| # | Field | Type | Required | Description |
|---|-------|------|----------|-------------|
| 1 | title | string | yes | Descriptive 5-8 word session name |
| 2 | summary | string | yes | 3-5 sentence summary (vectorized for semantic search) |
| 3 | sentiment | keyword | yes | User sentiment: positive, negative, mixed, neutral |
| 4 | sentiment_intensity | keyword | yes | Intensity: low, medium, high |
| 5 | topics | keyword_array | yes | 1-5 specific topics discussed |
| 6 | session_outcome | keyword | yes | resolved, unresolved, escalated, abandoned |
| 7 | user_intent | string | yes | What the user really needed (1-2 sentences) |
| 8 | risk_signals | keyword_array | no | Detected risk signals (frustration, churn_risk, complaint...) |
| 9 | key_entities | keyword_array | no | People, products, dates, amounts mentioned |
| 10 | action_items | string_array | no | Explicit commitments or next steps |

## Support Schema (+6 fields = 16 total)

For customer support conversations.

| # | Field | Type | Required | Values |
|---|-------|------|----------|--------|
| 11 | satisfaction_prediction | keyword | yes | very_satisfied, satisfied, neutral, dissatisfied, very_dissatisfied |
| 12 | issue_category | keyword | yes | billing, technical, account, product_inquiry, feature_request, bug_report, complaint, onboarding, cancellation, other |
| 13 | escalation_needed | boolean | yes | true/false |
| 14 | resolution_quality | keyword | yes | excellent, good, adequate, poor, failed |
| 15 | first_contact_resolution | boolean | yes | true/false |
| 16 | customer_effort_score | keyword | yes | very_low, low, medium, high, very_high |

## Sales Schema (+6 fields = 16 total)

For sales and prospecting conversations.

| # | Field | Type | Required | Values |
|---|-------|------|----------|--------|
| 11 | buying_stage | keyword | yes | awareness, consideration, decision, negotiation, closed_won, closed_lost |
| 12 | objections | string_array | no | Open — specific objections raised |
| 13 | budget_signals | keyword_array | yes | has_budget, no_budget, budget_unclear, price_sensitive, comparing_options |
| 14 | decision_urgency | keyword | yes | immediate, short_term, medium_term, long_term, no_urgency |
| 15 | competitive_mentions | keyword_array | no | Open — competitor names mentioned |
| 16 | next_best_action | string | yes | Specific next step for the sales team |

## Coaching Schema (+8 fields = 18 total)

For coaching, therapeutic, and personal development conversations.

| # | Field | Type | Required | Values |
|---|-------|------|----------|--------|
| 11 | emotional_valence | keyword | yes | very_positive, positive, neutral, negative, very_negative |
| 12 | emotional_intensity | keyword | yes | minimal, low, moderate, high, extreme |
| 13 | progress_indicators | string_array | no | Open — concrete signs of progress |
| 14 | behavioral_patterns | keyword_array | yes | avoidance, engagement, resistance, openness, rumination, catastrophizing, self_blame, growth_mindset, help_seeking, isolation |
| 15 | growth_markers | string_array | no | Open — insights and growth indicators |
| 16 | therapeutic_momentum | keyword | yes | accelerating, steady, stalled, regressing |
| 17 | adaptation_level | keyword | yes | thriving, coping, struggling, crisis |
| 18 | coping_strategies | keyword_array | yes | problem_solving, emotional_regulation, social_support, cognitive_reframing, avoidance, distraction, substance_use, physical_activity, mindfulness, creative_expression |

## Creating Custom Schemas

Create a YAML file in `src/analyxa/schemas/` (or a custom directory via `ANALYXA_SCHEMAS_DIR`):

```yaml
metadata:
  name: my_schema
  version: "1.0"
  description: "Description of your schema"
  inherits: universal  # Gets all 10 universal fields

fields:
  - name: my_custom_field
    type: keyword          # string, keyword, keyword_array, string_array, number, boolean
    required: true
    description: "Short description for documentation"
    prompt_hint: "Detailed instructions for the LLM — be specific about what to extract and how"
    allowed_values: [option_a, option_b, option_c]  # Only for keyword/keyword_array
```

### Field Types

| Type | JSON Output | Example |
|------|-------------|---------|
| string | `"text"` | Free text |
| keyword | `"value"` | Single value from allowed list |
| keyword_array | `["a", "b"]` | Multiple values from allowed list |
| string_array | `["text1", "text2"]` | Multiple free text values |
| number | `42` | Numeric value |
| boolean | `true` | True/false |

### Tips for Good prompt_hints

- Be specific: "Extract the user's emotional state" > "Get sentiment"
- Give examples: "e.g., 'billing', 'refund', NOT generic like 'problem'"
- Set boundaries: "Only include signals with clear evidence in the text"
- Clarify edge cases: "If the user starts negative but ends positive, classify by dominant state"
