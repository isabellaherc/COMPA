# Compa — API & Integration Contract Layer

> **Hackathon constraint**: n8n Cloud trial (no self-hosted), ElevenLabs Conversational AI + Twilio, Codex/OpenAI.
> All webhooks must be idempotent-safe, fast (sub-second LLM calls), and auditable.

---

## Table of Contents

1. [Authentication Scheme](#1-authentication-scheme)
2. [retar_decision Endpoint](#2-retar_decision-endpoint)
3. [correr_subasta Endpoint](#3-correr_subasta-endpoint)
4. [ElevenLabs Outbound Call API](#4-elevenlabs-outbound-call-api)
5. [n8n → ElevenLabs Integration](#5-n8n--elevenlabs-integration)
6. [ElevenLabs → n8n Integration](#6-elevenlabs--n8n-integration)
7. [Error Contracts](#7-error-contracts)
8. [Timeout & Retry Strategy](#8-timeout--retry-strategy)
9. [Security Checklist](#9-security-checklist)

---

## 1. Authentication Scheme

### 1.1 Credential Matrix

| Direction | Method | Header/Param | Source |
|---|---|---|---|
| n8n → ElevenLabs | Static API Key | `xi-api-key: sk_xxx` | ElevenLabs dashboard |
| ElevenLabs → n8n (webhook) | Static Bearer Token | `Authorization: Bearer whsec_xxx` | n8n webhook settings |
| n8n → Codex/OpenAI | Static API Key | `Authorization: Bearer sk-xxx` | OpenAI dashboard |

### 1.2 Key Management (n8n)

Store all credentials as **n8n Credentials** (not environment variables in workflow JSON):

```jsonc
// n8n credential: "ElevenLabs API"
{
  "name": "ElevenLabs API",
  "type": "headerAuth",
  "data": {
    "name": "xi-api-key",
    "value": "{{ $env.ELEVENLABS_API_KEY }}"
  }
}

// n8n credential: "Codex OpenAI"
{
  "name": "Codex OpenAI",
  "type": "oAuth2Api",
  "data": {
    "apiKey": "{{ $env.OPENAI_API_KEY }}"
  }
}

// n8n credential: "Webhook Auth"
// Used by ElevenLabs tools to authenticate to n8n
// Stored as a static bearer credential or a custom header credential
{
  "name": "Compa Webhook Auth",
  "type": "headerAuth",
  "data": {
    "name": "Authorization",
    "value": "Bearer whsec_compa_local_dev_2026"
  }
}
```

### 1.3 Webhook URL Convention

```
https://<workspace>.app.n8n.cloud/webhook/<webhook-id>
https://<workspace>.app.n8n.cloud/webhook-test/<webhook-id>   # test mode
```

The `webhook` vs `webhook-test` distinction avoids accidental production firings. In hour 0-2 of setup, register both and switch to `webhook` before the demo.

---

## 2. retar_decision Endpoint

### 2.1 Purpose

Called by the ElevenLabs agent when a producer describes a decision they need to make (e.g., "should I bid on this tender?"). The endpoint uses Codex to generate 3 tough, critical questions (the "cofounder" pattern) and returns them.

### 2.2 Endpoint Definition

```
POST https://<workspace>.app.n8n.cloud/webhook/<webhook-id>/retar-decision
Content-Type: application/json
Authorization: Bearer whsec_compa_<env>_<suffix>
```

### 2.3 Request Schema (JSON)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "RetarDecisionRequest",
  "type": "object",
  "required": [
    "decision_descrita",
    "contexto"
  ],
  "properties": {
    "decision_descrita": {
      "type": "string",
      "description": "The producer's description of the decision they are facing, transcribed from the ElevenLabs conversation.",
      "minLength": 10,
      "maxLength": 5000,
      "examples": [
        "El productor dice: 'He visto una licitacion de la alcaldia de Santa Tecla para proveer 500 uniformes escolares. El monto es de $12,000. Tengo capacidad para producirlos pero no estoy seguro si el margen es suficiente porque los materiales subieron de precio.'"
      ]
    },
    "contexto": {
      "type": "object",
      "description": "Contextual information n8n has about the producer and opportunity.",
      "required": ["productor_id", "oportunidad_id", "nombre_productor", "rubro"],
      "properties": {
        "productor_id": {
          "type": "string",
          "description": "Internal ID of the producer.",
          "examples": ["prod_001", "prod_023"]
        },
        "oportunidad_id": {
          "type": "string",
          "description": "Internal ID of the matched opportunity.",
          "examples": ["opp_045", "opp_102"]
        },
        "nombre_productor": {
          "type": "string",
          "description": "Producer's full name for personalization.",
          "examples": ["Maria Santos", "Carlos Rivera"]
        },
        "rubro": {
          "type": "string",
          "description": "Business category used for matching.",
          "examples": ["Confeccion textil", "Alimentos procesados"]
        },
        "monto_oportunidad": {
          "type": "number",
          "description": "Total contract value of the opportunity.",
          "examples": [12000.00, 85000.00]
        },
        "institucion": {
          "type": "string",
          "description": "Government institution publishing the opportunity.",
          "examples": ["Alcaldia de Santa Tecla", "MINED"]
        },
        "idioma": {
          "type": "string",
          "description": "Language/locale for Codex prompt.",
          "enum": ["es-SV", "es", "en"],
          "default": "es-SV"
        }
      }
    },
    "trace_id": {
      "type": "string",
      "description": "Correlation ID for observability across the entire call flow.",
      "pattern": "^[a-f0-9]{32}$",
      "examples": ["a1b2c3d4e5f6789012345678abcdef01"]
    }
  }
}
```

**Minimal working example:**

```json
{
  "decision_descrita": "He visto una licitacion de la alcaldia de Santa Tecla para proveer 500 uniformes escolares. El monto es de $12,000. Tengo capacidad para producirlos pero no estoy seguro si el margen es suficiente.",
  "contexto": {
    "productor_id": "prod_001",
    "oportunidad_id": "opp_045",
    "nombre_productor": "Maria Santos",
    "rubro": "Confeccion textil",
    "monto_oportunidad": 12000.00,
    "institucion": "Alcaldia de Santa Tecla"
  },
  "trace_id": "a1b2c3d4e5f6789012345678abcdef01"
}
```

### 2.4 Response Schema (200 Success)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "RetarDecisionResponse",
  "type": "object",
  "required": ["preguntas", "resumen"],
  "properties": {
    "preguntas": {
      "type": "array",
      "description": "Three hard questions generated by Codex, ordered from most critical to least.",
      "minItems": 3,
      "maxItems": 3,
      "items": {
        "type": "object",
        "required": ["pregunta", "intencion", "palabras_clave"],
        "properties": {
          "pregunta": {
            "type": "string",
            "description": "The question exactly as the agent should read aloud. Written in Salvadoran Spanish, direct tone.",
            "maxLength": 500,
            "examples": [
              "Maria, ya calculaste cuanto te cuesta producir cada uniforme con los precios actuales de tela y botones?",
              "Ya tienes experiencia vendiendole a una alcaldia o este seria tu primer contrato con el gobierno?"
            ]
          },
          "intencion": {
            "type": "string",
            "description": "What the question is trying to uncover. Used by n8n for logging, not sent to the agent.",
            "examples": [
              "Verificar si el productor tiene un calculo de costos real",
              "Evaluar experiencia previa con compras gubernamentales"
            ]
          },
          "palabras_clave": {
            "type": "array",
            "description": "Keywords the agent should listen for in the producer's answer.",
            "minItems": 1,
            "maxItems": 5,
            "items": {
              "type": "string"
            },
            "examples": [
              ["costos", "tela", "produccion", "margen"],
              ["alcaldia", "experiencia", "contrato"]
            ]
          }
        }
      }
    },
    "resumen": {
      "type": "string",
      "description": "One-sentence executive summary n8n may log for history.",
      "maxLength": 300,
      "examples": [
        "Se generaron 3 preguntas sobre rentabilidad, experiencia gubernamental y capacidad de entrega para la oportunidad de uniformes escolares de $12,000."
      ]
    },
    "trace_id": {
      "type": "string",
      "description": "Same correlation ID from the request, echoed back.",
      "examples": ["a1b2c3d4e5f6789012345678abcdef01"]
    }
  }
}
```

**Example success response:**

```json
{
  "preguntas": [
    {
      "pregunta": "Maria, ya calculaste cuanto te cuesta producir cada uniforme con los precios actuales de tela y botones?",
      "intencion": "Verificar si el productor tiene calculo de costos real",
      "palabras_clave": ["costos", "tela", "produccion", "margen"]
    },
    {
      "pregunta": "Has trabajado antes con una alcaldia o este seria tu primer contrato con el gobierno?",
      "intencion": "Evaluar experiencia en compras publicas",
      "palabras_clave": ["alcaldia", "experiencia", "contrato"]
    },
    {
      "pregunta": "Si ganas la licitacion, en cuanto tiempo podrias entregar los 500 uniformes?",
      "intencion": "Evaluar capacidad operativa y cadena de suministro",
      "palabras_clave": ["entrega", "plazo", "capacidad", "500"]
    }
  ],
  "resumen": "Se generaron preguntas sobre costos, experiencia gubernamental y capacidad de entrega.",
  "trace_id": "a1b2c3d4e5f6789012345678abcdef01"
}
```

### 2.5 Error Response Schemas

See [Section 7 — Error Contracts](#7-error-contracts) for the shared error body schema.

| HTTP Status | Condition | Meaning |
|---|---|---|
| `200` | Success | Questions generated and returned |
| `400` | Missing required fields | `decision_descrita` empty or `contexto` incomplete |
| `401` | Invalid/missing token | Wrong or absent `Authorization` header |
| `408` | Codex timeout > 15s | LLM call exceeded timeout |
| `422` | Codex returned malformed JSON | Parsed but didn't match `{ preguntas: [...] }` shape |
| `500` | Internal n8n error | Unexpected workflow failure |
| `502` | Codex API unreachable | OpenAI API down or rate-limited |
| `504` | Gateway timeout | n8n Cloud worker timed out (>30s total) |

### 2.6 Timeout Strategy

```yaml
n8n webhook node settings:
  Response Mode: "When Last Node Finishes"   # synchronous
  Response Timeout: 25 seconds               # n8n Cloud max is 30s

Codex (OpenAI) call inside webhook:
  Model: gpt-4o-mini                         # fast, cheap for structured prompt
  Max Tokens: 1024
  Temperature: 0.7
  Timeout: 15 seconds                        # per-request timeout in n8n HTTP Request node
  Max Retries: 1                             # one retry on 429 or 5xx

Fallback: If Codex does not respond within 15 seconds, n8n returns
          HTTP 408 with a static fallback question set (hardcoded).
```

---

## 3. correr_subasta Endpoint

### 3.1 Purpose

Called by the ElevenLabs agent when a producer asks to get quotes for a specific input. Simulates a reverse auction among suppliers using Codex to model each supplier's behavior over successive rounds. The agent reads the winner announcement aloud.

### 3.2 Endpoint Definition

```
POST https://<workspace>.app.n8n.cloud/webhook/<webhook-id>/correr-subasta
Content-Type: application/json
Authorization: Bearer whsec_compa_<env>_<suffix>
```

### 3.3 Request Schema (JSON)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "CorrerSubastaRequest",
  "type": "object",
  "required": [
    "insumo",
    "precio_inicial",
    "proveedores"
  ],
  "properties": {
    "insumo": {
      "type": "string",
      "description": "The product or service the producer wants to procure.",
      "minLength": 3,
      "maxLength": 500,
      "examples": [
        "500 uniformes escolares, talla infantil, tela poliester-algodon",
        "100 quintales de maiz blanco para pupusas"
      ]
    },
    "precio_inicial": {
      "type": "number",
      "description": "The starting price the producer is willing to pay (in USD). Acts as the ceiling for the auction.",
      "minimum": 1,
      "maximum": 1000000,
      "examples": [12000.00, 8500.50]
    },
    "proveedores": {
      "type": "array",
      "description": "List of suppliers that will participate in the simulated auction.",
      "minItems": 2,
      "maxItems": 10,
      "items": {
        "type": "object",
        "required": ["nombre", "rubro"],
        "properties": {
          "nombre": {
            "type": "string",
            "description": "Supplier name.",
            "maxLength": 200,
            "examples": ["Textiles El Sol", "Confecciones Sivar"]
          },
          "rubro": {
            "type": "string",
            "description": "Supplier's business category.",
            "examples": ["Confeccion textil", "Alimentos"]
          },
          "ubicacion": {
            "type": "string",
            "description": "Supplier's location.",
            "examples": ["San Salvador", "Santa Tecla"]
          },
          "personalidad": {
            "type": "string",
            "description": "Optional personality trait Codex should use when simulating this supplier's bidding.",
            "examples": ["agresivo", "conservador", "estrategico"],
            "default": "estrategico"
          }
        }
      }
    },
    "contexto": {
      "type": "object",
      "description": "Additional context for logging.",
      "properties": {
        "productor_id": { "type": "string" },
        "oportunidad_id": { "type": "string" },
        "nombre_productor": { "type": "string" },
        "rondas_max": {
          "type": "integer",
          "description": "Maximum number of auction rounds before force-stop.",
          "minimum": 1,
          "maximum": 10,
          "default": 5
        }
      }
    },
    "trace_id": {
      "type": "string",
      "pattern": "^[a-f0-9]{32}$"
    }
  }
}
```

**Minimal working example:**

```json
{
  "insumo": "500 uniformes escolares, talla infantil, tela poliester-algodon",
  "precio_inicial": 12000.00,
  "proveedores": [
    {
      "nombre": "Textiles El Sol",
      "rubro": "Confeccion textil",
      "ubicacion": "San Salvador",
      "personalidad": "agresivo"
    },
    {
      "nombre": "Confecciones Sivar",
      "rubro": "Confeccion textil",
      "ubicacion": "Santa Tecla",
      "personalidad": "conservador"
    },
    {
      "nombre": "Uniformex Centroamerica",
      "rubro": "Confeccion textil",
      "ubicacion": "San Miguel",
      "personalidad": "estrategico"
    }
  ],
  "contexto": {
    "productor_id": "prod_001",
    "oportunidad_id": "opp_045",
    "nombre_productor": "Maria Santos",
    "rondas_max": 5
  },
  "trace_id": "a1b2c3d4e5f6789012345678abcdef01"
}
```

### 3.4 Response Schema (200 Success)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "CorrerSubastaResponse",
  "type": "object",
  "required": ["ganador", "precio_final", "rondas", "historial"],
  "properties": {
    "ganador": {
      "type": "object",
      "description": "The winning supplier.",
      "required": ["nombre", "precio_ofertado", "ahorro"],
      "properties": {
        "nombre": { "type": "string", "examples": ["Textiles El Sol"] },
        "precio_ofertado": {
          "type": "number",
          "description": "Final price offered by the winner in USD.",
          "examples": [9800.00]
        },
        "ahorro": {
          "type": "number",
          "description": "Savings compared to initial price (precio_inicial - precio_ofertado).",
          "examples": [2200.00]
        },
        "mensaje_anuncio": {
          "type": "string",
          "description": "An announcement string the agent can read verbatim. Energetic, celebratory tone.",
          "maxLength": 300,
          "examples": [
            "El ganador es Textiles El Sol con una oferta de $9,800! Un ahorro de $2,200 comparado con tu presupuesto inicial. Buen negocio, Maria!"
          ]
        }
      }
    },
    "precio_final": {
      "type": "number",
      "description": "The final winning price (lowest bid).",
      "examples": [9800.00]
    },
    "rondas": {
      "type": "integer",
      "description": "Number of auction rounds actually completed.",
      "minimum": 1,
      "examples": [4]
    },
    "historial": {
      "type": "array",
      "description": "Full round-by-round history. Length equals `rondas`.",
      "items": {
        "type": "object",
        "required": ["ronda", "ofertas"],
        "properties": {
          "ronda": {
            "type": "integer",
            "description": "Round number (1-indexed)."
          },
          "ofertas": {
            "type": "array",
            "items": {
              "type": "object",
              "required": ["proveedor", "precio"],
              "properties": {
                "proveedor": { "type": "string", "description": "Supplier name." },
                "precio": { "type": "number", "description": "Bid in USD." },
                "sigue_compitiendo": {
                  "type": "boolean",
                  "description": "Whether the supplier dropped out after this round."
                },
                "comentario": {
                  "type": "string",
                  "description": "Short in-character justification from the supplier (for logging/entertainment)."
                }
              }
            }
          }
        }
      }
    },
    "resumen": {
      "type": "string",
      "description": "One-line summary for logging.",
      "examples": [
        "Subasta de 4 rondas: 3 proveedores, precio final $9,800, ahorro $2,200 (18.3%)."
      ]
    },
    "trace_id": {
      "type": "string",
      "examples": ["a1b2c3d4e5f6789012345678abcdef01"]
    }
  }
}
```

**Example success response:**

```json
{
  "ganador": {
    "nombre": "Textiles El Sol",
    "precio_ofertado": 9800.00,
    "ahorro": 2200.00,
    "mensaje_anuncio": "El ganador es Textiles El Sol con una oferta de $9,800! Un ahorro de $2,200 comparado con tu presupuesto inicial. Buen negocio, Maria!"
  },
  "precio_final": 9800.00,
  "rondas": 4,
  "historial": [
    {
      "ronda": 1,
      "ofertas": [
        { "proveedor": "Textiles El Sol", "precio": 11500.00, "sigue_compitiendo": true, "comentario": "Empezamos fuerte." },
        { "proveedor": "Confecciones Sivar", "precio": 11800.00, "sigue_compitiendo": true, "comentario": "Podemos igualar." },
        { "proveedor": "Uniformex Centroamerica", "precio": 11200.00, "sigue_compitiendo": true, "comentario": "Vamos a ganar esta." }
      ]
    },
    {
      "ronda": 2,
      "ofertas": [
        { "proveedor": "Textiles El Sol", "precio": 10700.00, "sigue_compitiendo": true, "comentario": "Bajamos $800." },
        { "proveedor": "Confecciones Sivar", "precio": 11200.00, "sigue_compitiendo": false, "comentario": "Llegamos a nuestro limite." },
        { "proveedor": "Uniformex Centroamerica", "precio": 10500.00, "sigue_compitiendo": true, "comentario": "Aun podemos mas." }
      ]
    },
    {
      "ronda": 3,
      "ofertas": [
        { "proveedor": "Textiles El Sol", "precio": 9950.00, "sigue_compitiendo": true, "comentario": "Ultima oferta." },
        { "proveedor": "Uniformex Centroamerica", "precio": 10200.00, "sigue_compitiendo": false, "comentario": "Nos retiramos, buen precio." }
      ]
    },
    {
      "ronda": 4,
      "ofertas": [
        { "proveedor": "Textiles El Sol", "precio": 9800.00, "sigue_compitiendo": false, "comentario": "Es nuestro mejor precio final." }
      ]
    }
  ],
  "resumen": "Subasta de 4 rondas: 3 proveedores, precio final $9,800, ahorro $2,200 (18.3%).",
  "trace_id": "a1b2c3d4e5f6789012345678abcdef01"
}
```

### 3.5 Stopping Conditions (inside n8n Codex loop)

| Condition | Action |
|---|---|
| Only 1 supplier remains | Declare winner immediately |
| All remaining suppliers pass (no one lowers) | Declare winner = lowest current bid |
| `rondas_max` reached | Force-stop, declare winner = lowest current bid |
| Precio reaches `< 60%` of `precio_inicial` | Flag as suspicious, force-stop, declare winner |
| A supplier bids higher than previous round | Remove them from competition |

### 3.6 Error Response Schemas

| HTTP Status | Condition | Meaning |
|---|---|---|
| `200` | Auction completed normally | Always returns a winner (even in edge cases) |
| `400` | Missing/empty `insumo`, `precio_inicial <= 0`, `< 2` proveedores | Validation failed |
| `401` | Invalid/missing token | Wrong or absent Authorization |
| `408` | Codex timeout after first round | Partial results returned with `rondas = 0` and a fallback winner |
| `422` | Codex LLM returned invalid JSON | Could not parse any round |
| `502` | Codex API unreachable | Fallback: pick random supplier at 5% discount |
| `504` | Gateway timeout | n8n Cloud circuit breaker |

---

## 4. ElevenLabs Outbound Call API

### 4.1 Purpose

n8n triggers an outbound phone call through ElevenLabs Conversational AI when a high-quality opportunity match is found. The call uses a configured agent with dynamic variables for personalization.

### 4.2 API Reference

```
POST https://api.elevenlabs.io/v1/convai/conversation
Content-Type: application/json
xi-api-key: {{ ELEVENLABS_API_KEY }}
```

> **Note**: As of 2026, ElevenLabs uses `POST /v1/convai/conversation` for outbound calls via the Conversational AI API. If the exact endpoint differs (e.g., `POST /v1/convai/outbound-calls`), the payload shape remains the same — verify against the current ElevenLabs API reference during setup.

### 4.3 Request Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "ElevenLabsOutboundCallRequest",
  "type": "object",
  "required": [
    "agent_id",
    "phone_number",
    "dynamic_variables"
  ],
  "properties": {
    "agent_id": {
      "type": "string",
      "description": "The ElevenLabs Agent ID (created in the ElevenLabs dashboard, Conversational AI > Agents).",
      "pattern": "^[a-zA-Z0-9]{24}$",
      "examples": ["agX7k2m9pQ4rL3zN8wB6vC1d"]
    },
    "phone_number": {
      "type": "string",
      "description": "The producer's phone number in E.164 format. ElevenLabs/Twilio will originate the call to this number.",
      "pattern": "^\\+[1-9]\\d{1,14}$",
      "examples": ["+50370001234", "+50361234567"]
    },
    "dynamic_variables": {
      "type": "object",
      "description": "Template variables that ElevenLabs injects into the agent's system prompt and first message. Must match `{{variable_name}}` placeholders in the agent configuration.",
      "required": ["nombre_productor", "rubro_negocio", "oportunidad_detectada"],
      "properties": {
        "nombre_productor": {
          "type": "string",
          "description": "Injected into the prompt as {{nombre_productor}}.",
          "maxLength": 100,
          "examples": ["Maria Santos", "Carlos Rivera"]
        },
        "rubro_negocio": {
          "type": "string",
          "description": "Injected into the prompt as {{rubro_negocio}}.",
          "maxLength": 200,
          "examples": ["Confeccion textil", "Panaderia artesanal"]
        },
        "oportunidad_detectada": {
          "type": "string",
          "description": "Injected into the prompt as {{oportunidad_detectada}}. Should be a concise, natural-language summary (not raw JSON).",
          "maxLength": 1000,
          "examples": [
            "Hay una licitacion de la Alcaldia de Santa Tecla por $12,000 para proveer 500 uniformes escolares. La fecha de cierre es el 15 de agosto.",
            "El Ministerio de Salud busca proveer 1000 canastas de alimentos basicos por $85,000. Cierre el 20 de agosto."
          ]
        },
        "voice_id_elevenlabs": {
          "type": "string",
          "description": "Optional. Override the agent's default voice. Maps to a specific ElevenLabs voice ID.",
          "pattern": "^[a-zA-Z0-9]{20}$",
          "examples": ["21m00Tcm4TlvDq8ikWAM"]
        },
        "oportunidad_id": {
          "type": "string",
          "description": "Optional. Internal tracking ID echoed in ElevenLabs webhook events.",
          "examples": ["opp_045"]
        },
        "productor_tono": {
          "type": "string",
          "description": "Optional. Communication style from perfil_llm to adjust the agent's tone.",
          "enum": ["directo", "formal", "pausado"],
          "default": "directo"
        }
      },
      "additionalProperties": false
    },
    "first_message": {
      "type": "string",
      "description": "Optional. The first thing the agent says when the call connects. If omitted, ElevenLabs uses the agent's configured first message. Override to keep it specific to this opportunity.",
      "maxLength": 500,
      "examples": [
        "Hola Maria, soy Compa, tu cofundador de IA. Te llamo porque vi una oportunidad bien interesante para tu negocio de confeccion textil. Tenes un momento para contartela?"
      ]
    },
    "webhook_events": {
      "type": "array",
      "description": "Optional. ElevenLabs event types to forward to the configured webhook URL. Helps n8n track call state.",
      "items": {
        "type": "string",
        "enum": [
          "call_started",
          "call_ended",
          "transcript_ready",
          "tool_executed",
          "error"
        ]
      },
      "default": ["call_ended", "tool_executed"]
    },
    "metadata": {
      "type": "object",
      "description": "Optional. Arbitrary metadata ElevenLabs will echo back in webhook events for correlation.",
      "properties": {
        "trace_id": { "type": "string" },
        "productor_id": { "type": "string" },
        "oportunidad_id": { "type": "string" }
      },
      "additionalProperties": true
    }
  },
  "additionalProperties": false
}
```

### 4.4 Response Schema (200 Created)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "ElevenLabsOutboundCallResponse",
  "type": "object",
  "required": ["conversation_id", "status"],
  "properties": {
    "conversation_id": {
      "type": "string",
      "description": "UUID assigned by ElevenLabs for tracking this call.",
      "examples": ["conv_abc123def456"]
    },
    "status": {
      "type": "string",
      "enum": ["queued", "initiating", "error"],
      "examples": ["queued"]
    },
    "estimated_wait_seconds": {
      "type": "integer",
      "description": "Estimated wait time before the call is placed.",
      "examples": [2]
    }
  }
}
```

### 4.5 Minimal Working Request (copy-paste for n8n HTTP Request node)

```json
{
  "agent_id": "agX7k2m9pQ4rL3zN8wB6vC1d",
  "phone_number": "+50370001234",
  "dynamic_variables": {
    "nombre_productor": "Maria Santos",
    "rubro_negocio": "Confeccion textil",
    "oportunidad_detectada": "Hay una licitacion de la Alcaldia de Santa Tecla por $12,000 para proveer 500 uniformes escolares. Cierre el 15 de agosto."
  },
  "first_message": "Hola Maria, soy Compa, tu cofundador de IA. Te llamo porque vi una oportunidad bien interesante para tu negocio de confeccion textil. Tenes un momento para contartela?",
  "metadata": {
    "trace_id": "a1b2c3d4e5f6789012345678abcdef01",
    "productor_id": "prod_001",
    "oportunidad_id": "opp_045"
  }
}
```

---

## 5. n8n → ElevenLabs Integration

### 5.1 Workflow: Oportunidades (Cron)

```
┌─────────────────────────────────────────────────────────┐
│  n8n Workflow: "Oportunidades"                          │
│                                                         │
│  Schedule: Cron (every 6 hours, or manual during demo)  │
│                                                         │
│  [Schedule Trigger]                                     │
│       │                                                │
│       ▼                                                │
│  [Read Dataset]  ← COMPRASAL cached CSV / Google Sheet  │
│       │                                                │
│       ▼                                                │
│  [Filter by Rubro]  ← match against productor perfil    │
│       │                                                │
│       ▼                                                │
│  [Loop over Matches]                                    │
│       │                                                │
│       ├── [HTTP Request] ──→ ElevenLabs API             │
│       │      POST /v1/convai/conversation               │
│       │      Headers: xi-api-key, Content-Type          │
│       │      Body: outbound call JSON (Section 4.3)     │
│       │                                                │
│       └── [Log to DB / Google Sheet]                    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 5.2 n8n HTTP Request Node Configuration

**Node type**: HTTP Request
**Method**: POST
**URL**: `https://api.elevenlabs.io/v1/convai/conversation`
**Authentication**: Header Auth (credential: "ElevenLabs API")
**Headers**:

| Header | Value |
|---|---|
| `Content-Type` | `application/json` |
| `xi-api-key` | From credential (do not inline) |

**JSON Body** (expression mode):

```javascript
// n8n expression for the HTTP Request body
// Assumes the loop item contains matchedData from the filter step
{
  "agent_id": "agX7k2m9pQ4rL3zN8wB6vC1d",
  "phone_number": "{{ $json.telefono }}",
  "dynamic_variables": {
    "nombre_productor": "{{ $json.nombre_productor }}",
    "rubro_negocio": "{{ $json.rubro }}",
    "oportunidad_detectada": "{{ $json.oportunidad_resumen }}"
  },
  "first_message": "Hola {{ $json.nombre_productor }}, soy Compa, tu cofundador de IA. Te llamo porque vi una oportunidad bien interesante para tu {{ $json.rubro }}. Tenes un momento para contartela?",
  "metadata": {
    "trace_id": "{{ $json.trace_id }}",
    "productor_id": "{{ $json.productor_id }}",
    "oportunidad_id": "{{ $json.oportunidad_id }}"
  },
  "webhook_events": ["call_ended", "tool_executed"]
}
```

### 5.3 Error Handling in n8n

```yaml
HTTP Request node error handling:
  - On 4xx: Log error + continue to next productor (don't stop the loop)
  - On 5xx: Retry 1 time with 2s delay, then log and continue
  - On timeout (5s): Log "ElevenLabs API timeout" and continue
  - Max calls per workflow run: 10 (rate limit safeguard)
```

---

## 6. ElevenLabs → n8n Integration

### 6.1 Agent Tool Configuration (ElevenLabs Dashboard)

In the ElevenLabs Conversational AI dashboard, under the agent's **Tools** section, configure two custom tools:

#### Tool 1: `retar_decision`

| Field | Value |
|---|---|
| **Tool Name** | `retar_decision` |
| **Description** | Call this when the producer describes a business decision they need to think through. Sends the description to an AI cofounder that generates critical questions. Returns an array of 3 questions with keywords to listen for. |
| **Method** | `POST` |
| **URL** | `https://<workspace>.app.n8n.cloud/webhook/<webhook-id>/retar-decision` |
| **Headers** | `Authorization: Bearer whsec_compa_<env>_<suffix>` |
| **Body** | JSON (see schema below) |
| **Tool Timeout** | 25 seconds |

**JSON Body template (filled by ElevenLabs agent runtime):**

```json
{
  "decision_descrita": "{{decision_descrita}}",
  "contexto": {
    "productor_id": "{{productor_id}}",
    "oportunidad_id": "{{oportunidad_id}}",
    "nombre_productor": "{{nombre_productor}}",
    "rubro": "{{rubro_negocio}}",
    "monto_oportunidad": {{monto_oportunidad}},
    "institucion": "{{institucion}}"
  },
  "trace_id": "{{trace_id}}"
}
```

**Parameter definitions (configured in ElevenLabs Tools UI):**

| Parameter Name | Type | Required | Description | Example |
|---|---|---|---|---|
| `decision_descrita` | string | yes | The producer's own words describing their decision | "He visto una licitacion para uniformes escolares..." |
| `productor_id` | string | yes | Internal productor ID | "prod_001" |
| `oportunidad_id` | string | yes | Internal opportunity ID | "opp_045" |
| `nombre_productor` | string | yes | Producer name for context | "Maria Santos" |
| `rubro_negocio` | string | yes | Business category | "Confeccion textil" |
| `monto_oportunidad` | number | no | Contract value | 12000.00 |
| `institucion` | string | no | Institution name | "Alcaldia de Santa Tecla" |
| `trace_id` | string | no | Correlation ID (n8n generates if omitted) | "a1b2c3d4e5f6789012345678abcdef01" |

#### Tool 2: `correr_subasta`

| Field | Value |
|---|---|
| **Tool Name** | `correr_subasta` |
| **Description** | Call this when the producer asks to get quotes or start an auction for a specific product. Simulates competitive bidding among suppliers. Returns a winner with final price. |
| **Method** | `POST` |
| **URL** | `https://<workspace>.app.n8n.cloud/webhook/<webhook-id>/correr-subasta` |
| **Headers** | `Authorization: Bearer whsec_compa_<env>_<suffix>` |
| **Body** | JSON (see schema below) |
| **Tool Timeout** | 25 seconds |

**JSON Body template:**

```json
{
  "insumo": "{{insumo}}",
  "precio_inicial": {{precio_inicial}},
  "proveedores": {{proveedores}},
  "contexto": {
    "productor_id": "{{productor_id}}",
    "oportunidad_id": "{{oportunidad_id}}",
    "nombre_productor": "{{nombre_productor}}",
    "rondas_max": 5
  },
  "trace_id": "{{trace_id}}"
}
```

**Parameter definitions:**

| Parameter Name | Type | Required | Description | Example |
|---|---|---|---|---|
| `insumo` | string | yes | Product/service to procure | "500 uniformes escolares" |
| `precio_inicial` | number | yes | Maximum price willing to pay | 12000.00 |
| `proveedores` | array | yes | List of supplier objects (see Section 3.3) | `[{"nombre":"...","rubro":"..."}]` |
| `productor_id` | string | yes | Internal ID | "prod_001" |
| `oportunidad_id` | string | no | Opportunity this auction is for | "opp_045" |
| `nombre_productor` | string | yes | For personalization | "Maria Santos" |
| `trace_id` | string | no | Correlation ID | "a1b2c3d4e5f6789012345678abcdef01" |

### 6.2 ElevenLabs Agent Response Handling

When ElevenLabs executes a tool, the tool's HTTP response is returned to the agent.
The agent's system prompt must instruct it how to use the results.

**System prompt excerpt for tool responses:**

```
Herramientas disponibles:
- retar_decision: Devuelve { preguntas: [{ pregunta, intencion, palabras_clave }] }.
  Despues de recibir las preguntas, leelas UNA POR UNA. Lee la primera, espera respuesta,
  luego lee la segunda, espera respuesta, luego la tercera. Las palabras_clave en cada
  pregunta te ayudan a identificar si el productor ya respondio.

- correr_subasta: Devuelve { ganador: { nombre, precio_ofertado, mensaje_anuncio } }.
  Lee el mensaje_anuncio textualmente con energia de presentador. No lo resumas —
  leelo completo.
```

### 6.3 Testing Tool Calls (n8n Webhook Test Mode)

During development, ElevenLabs tools call `webhook-test` URLs:

```text
Production: POST https://workspace.app.n8n.cloud/webhook/abc123/retar-decision
Test:       POST https://workspace.app.n8n.cloud/webhook-test/abc123/retar-decision
```

The n8n workflow must be in **"Inactive" → "Webhook" → "Active"** state for production endpoints, or have the **webhook listener running** for test endpoints (n8n UI must be open on that workflow tab).

**Debugging tip**: Use n8n's **"Execute Workflow"** button on the webhook node and inspect the last execution to see the raw request/response.

---

## 7. Error Contracts

### 7.1 Shared Error Response Schema

Every endpoint returns the same error envelope so the ElevenLabs agent can parse it uniformly:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "CompaErrorResponse",
  "type": "object",
  "required": ["error", "codigo", "mensaje"],
  "properties": {
    "error": {
      "type": "boolean",
      "const": true,
      "description": "Always true for error responses."
    },
    "codigo": {
      "type": "string",
      "description": "Machine-readable error code. Use dot-notation for hierarchy.",
      "examples": [
        "VALIDATION.REQUIRED_FIELD",
        "AUTH.INVALID_TOKEN",
        "CODEX.TIMEOUT",
        "CODEX.MALFORMED_RESPONSE",
        "CODEX.UNAVAILABLE",
        "INTERNAL.SERVER_ERROR",
        "TIMEOUT.GATEWAY"
      ]
    },
    "mensaje": {
      "type": "string",
      "description": "Human-readable error description in Spanish (for agent consumption).",
      "maxLength": 300,
      "examples": [
        "Falta el campo requerido: decision_descrita",
        "No se pudieron generar preguntas en este momento. Intente de nuevo.",
        "El servicio de inteligencia artificial no esta disponible. Use preguntas de respaldo."
      ]
    },
    "detalles": {
      "type": "object",
      "description": "Optional. Additional structured error context.",
      "properties": {
        "campo": { "type": "string", "description": "Which field failed validation." },
        "razon": { "type": "string", "description": "Specific validation failure reason." },
        "fallback_usado": { "type": "boolean", "description": "Whether n8n served a fallback response." }
      },
      "additionalProperties": true
    },
    "trace_id": {
      "type": "string",
      "description": "Correlation ID for cross-system debugging.",
      "examples": ["a1b2c3d4e5f6789012345678abcdef01"]
    }
  }
}
```

### 7.2 Error Code Catalog

| Code | HTTP Status | Meaning | Agent Behavior |
|---|---|---|---|
| `VALIDATION.REQUIRED_FIELD` | 400 | A required field is missing or empty | Apologize, ask the producer to clarify |
| `VALIDATION.INVALID_VALUE` | 400 | Field value out of range (e.g., `precio_inicial <= 0`) | Explain the constraint, ask for correction |
| `VALIDATION.MIN_PROVEEDORES` | 400 | `proveedores` must have at least 2 entries | Ask the producer to name at least 2 suppliers |
| `AUTH.INVALID_TOKEN` | 401 | Authorization header missing or wrong | Log error, apologise generically ("problema tecnico") |
| `AUTH.EXPIRED_TOKEN` | 401 | Token has been revoked/rotated | Same as above |
| `CODEX.TIMEOUT` | 408 | OpenAI did not respond within 15s | Use fallback questions / announce fallback winner |
| `CODEX.MALFORMED_RESPONSE` | 422 | OpenAI responded but JSON was invalid | Use fallback data |
| `CODEX.UNAVAILABLE` | 502 | OpenAI API returned 5xx or network error | Use fallback data |
| `RATE_LIMIT.CODEX` | 429 | OpenAI rate limit hit (retried 1x, still failed) | Same as CODEX.TIMEOUT |
| `RATE_LIMIT.ELEVENLABS` | 429 | ElevenLabs rate limit hit | Log, n8n stops the loop |
| `INTERNAL.SERVER_ERROR` | 500 | Unexpected n8n workflow failure | Generic apology, hang up politely |
| `TIMEOUT.GATEWAY` | 504 | n8n Cloud worker exceeded 30s limit | Generic apology |

### 7.3 Example Error Responses

**Validation error (400):**

```json
{
  "error": true,
  "codigo": "VALIDATION.REQUIRED_FIELD",
  "mensaje": "Falta el campo requerido: decision_descrita. Proporcione una descripcion de la decision.",
  "detalles": {
    "campo": "decision_descrita",
    "razon": "El campo no puede estar vacio o ausente."
  },
  "trace_id": "a1b2c3d4e5f6789012345678abcdef01"
}
```

**Auth error (401):**

```json
{
  "error": true,
  "codigo": "AUTH.INVALID_TOKEN",
  "mensaje": "Token de autenticacion invalido o ausente.",
  "detalles": {
    "razon": "El header Authorization no contiene un token valido."
  },
  "trace_id": null
}
```

**Codex timeout (408) — with fallback data:**

```json
{
  "error": true,
  "codigo": "CODEX.TIMEOUT",
  "mensaje": "No se pudieron generar preguntas personalizadas en este momento. Usando preguntas de respaldo.",
  "detalles": {
    "fallback_usado": true
  },
  "fallback_data": {
    "preguntas": [
      {
        "pregunta": "Ya calculaste cuanto te cuesta producir esto?",
        "intencion": "Evaluacion de costos",
        "palabras_clave": ["costo", "producir"]
      },
      {
        "pregunta": "Tenes experiencia en este tipo de contrato?",
        "intencion": "Experiencia previa",
        "palabras_clave": ["experiencia", "contrato"]
      },
      {
        "pregunta": "En cuanto tiempo podrias entregar?",
        "intencion": "Capacidad operativa",
        "palabras_clave": ["tiempo", "entrega"]
      }
    ]
  },
  "trace_id": "a1b2c3d4e5f6789012345678abcdef01"
}
```

**NOTE**: The `fallback_data` field is NOT part of the error envelope schema — it is an undocumented extension used only by the `CODEX.TIMEOUT` and `CODEX.UNAVAILABLE` codes. The ElevenLabs agent's system prompt must instruct it to inspect `error.fallback_data` when present.

---

## 8. Timeout & Retry Strategy

### 8.1 End-to-End Timing Budget

```
ElevenLabs Tool Timeout: 25s
    │
    ├── n8n Webhook Timeout: 23s  (25s - 2s safety margin)
    │       │
    │       ├── n8n Input Validation: < 100ms
    │       │
    │       ├── OpenAI (Codex) Call: 15s timeout, 1 retry
    │       │       │
    │       │       ├── First attempt: 15s
    │       │       ├── Retry (if 429/5xx): 15s
    │       │       └── Total worst-case: 30s → cut short by webhook timeout
    │       │
    │       ├── n8n Loop Iterations (subasta only): 5 rounds × ~3s = 15s
    │       │       └── Each Codex call: 2.5s timeout (smaller prompt for single supplier)
    │       │
    │       └── Response Assembly: < 50ms
    │
    └── Total n8n processing: 15-20s typical, 23s max
```

### 8.2 n8n Node Timeout Configuration

```yaml
Webhook Node:
  Response Mode: "When Last Node Finishes"     # synchronous
  Response Timeout: 25 seconds                 # must be < ElevenLabs 25s tool timeout

HTTP Request (→ OpenAI):
  Timeout: 15 seconds                          # per-request
  Retry on Fail: true
  Max Retries: 1
  Retry Delay: 500ms
  Retry on Status: [408, 429, 500, 502, 503]

HTTP Request (→ ElevenLabs inbound — not used here):
  Timeout: 5 seconds                           # ElevenLabs API is fast
  Retry on Fail: true
  Max Retries: 1
```

### 8.3 n8n Workflow Retry Strategy

```yaml
Subasta loop Codex calls:
  Timeout: 3 seconds per supplier call
  Retries: 0                                   # faster to skip one round than retry in auction
  If a single round fails: skip that round, keep going
  If 2+ consecutive rounds fail: stop loop, declare current lowest as winner

Cron trigger (Oportunidades):
  Retry on Failure: true
  Max Retries: 1
  Retry Interval: 60 seconds                   # wait before retrying the entire cron run
```

### 8.4 ElevenLabs Tool Retry Strategy

ElevenLabs is the caller. It will use its built-in HTTP retry:

```yaml
ElevenLabs tool execution:
  - On HTTP 4xx: DO NOT retry. Log the error, agent apologizes and pivots conversation.
  - On HTTP 5xx: Retry 1 time after 2 second delay.
  - On HTTP 408 (timeout): Use fallback data from the response body (see Section 7.3).
  - On network error (connection refused, DNS failure): Do NOT retry.
    Agent says "Estoy teniendo problemas tecnicos, mejor te llamo despues. Disculpa."
  - Max total tool time from ElevenLabs: 25 seconds (configured in agent settings).
    If the tool takes longer, ElevenLabs cancels it and the agent gets an error.
```

### 8.5 n8n Webhook Test Mode Timeout

```yaml
n8n webhook-test:
  - Timeout: 30 seconds (n8n allows longer in test mode)
  - Use during development only
  - After deploying, switch to webhook (production) with 25s timeout
```

---

## 9. Security Checklist

| # | Item | Status (pre-demo) |
|---|---|---|
| 1 | All n8n webhooks use `Authorization: Bearer` (not query-param tokens) | |
| 2 | ElevenLabs API key stored in n8n Credentials, never in workflow JSON | |
| 3 | OpenAI API key stored in n8n Credentials | |
| 4 | Webhook URLs use `webhook/` (production), not `webhook-test/` | |
| 5 | ElevenLabs agent is restricted to calling only the 2 tool URLs | |
| 6 | `trace_id` generated for every outbound call (UUID4 or MD5 of timestamp+productor) | |
| 7 | Auditing: every webhook execution logged to Google Sheet or Airtable | |
| 8 | No secrets committed to repo (use `.env.example` with placeholder values) | |
| 9 | All dynamic_variables validated client-side (ElevenLabs) — no injection possible | |
| 10 | `precio_inicial` capped at 1,000,000 USD | |
| 11 | `proveedores` array limited to 10 items | |
| 12 | Webhook CSRF: reject requests without `Content-Type: application/json` | |

---

## Quick Reference: All Endpoints

| Direction | Endpoint | Method | Auth | Purpose |
|---|---|---|---|---|
| ElevenLabs → n8n | `POST /webhook/<id>/retar-decision` | POST | Bearer `whsec_*` | Generate 3 critical questions |
| ElevenLabs → n8n | `POST /webhook/<id>/correr-subasta` | POST | Bearer `whsec_*` | Simulate reverse auction |
| n8n → ElevenLabs | `POST /v1/convai/conversation` | POST | `xi-api-key` | Trigger outbound phone call |
| n8n → OpenAI | `POST /v1/chat/completions` | POST | Bearer `sk-*` | Structured LLM reasoning |

---

*Document version 1.0 — 2026-07-04 — Compa Buildathon*
