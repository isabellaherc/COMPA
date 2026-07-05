# Compa — Contexto completo para diseño de arquitectura

## Qué es Compa

Compa es un "socio" digital con voz para MYPE y cooperativas salvadoreñas que venden al Estado. Detecta oportunidades de negocio en COMPRASAL, las explica por voz (ElevenLabs), ayuda a decidir si conviene participar, y organiza cotizaciones entre proveedores.

## Stack tecnológico obligatorio (3 tecnologías)

1. **n8n** — orquestación de todos los flujos (workflows: cron, webhooks, loops)
2. **ElevenLabs Conversational AI** — voz del agente + telefonía (Twilio inbound/outbound)
3. **Codex/OpenAI** — razonamiento estructurado (clasificación, generación de preguntas, simulación de proveedores)

## Los tres módulos

| Módulo | Prioridad | Qué hace |
|---|---|---|
| **Oportunidades** | Alta | Detecta oportunidades de COMPRASAL que matchean el perfil del productor, lo llama por teléfono |
| **Cofundador** | Alta | Recibe descripción de decisión del productor, genera 3 preguntas duras, las lee una por una |
| **Subasta Inversa** | Baja (stretch) | Simula subasta entre proveedores con rondas sucesivas, anuncia ganador |

## Arquitectura actual (conceptual)

```
COMPRASAL (dataset cacheado)
        ↓
   n8n Workflow "Oportunidades" (cron)
        ↓
   Match rubro vs perfil productor (Airtable/Google Sheets)
        ↓
   ElevenLabs outbound call (Twilio) con dynamic_variables
        ↓
   Productor recibe llamada → conversa con Compa
        ↓
   Si describe decisión → n8n webhook "retar_decision" → Codex genera 3 preguntas
   Si pide cotizar → n8n webhook "correr_subasta" → Codex simula proveedores
```

## Tools del agente ElevenLabs

| Tool | Parámetros | Webhook n8n |
|---|---|---|
| `retar_decision` | `decision_descrita` (string) | POST /retar-decision |
| `correr_subasta` | `insumo` (string), `precio_inicial` (number), `proveedores` (array) | POST /correr-subasta |

## Workflows n8n requeridos

1. **Oportunidades** (cron): lee dataset cacheado COMPRASAL → match por rubro → POST outbound call ElevenLabs con dynamic_variables
2. **Cofundador / retar_decision** (webhook): recibe `decision_descrita` → HTTP Request a Codex con prompt cofundador → parsea `{ preguntas: [...] }` → responde al agente
3. **Subasta Inversa / correr_subasta** (webhook): recibe insumo + proveedores → loop de rondas con Codex simulando cada proveedor → corta cuando nadie baja más → devuelve `{ ganador, precio_final }`

## Modelo de datos mínimo

```sql
productores(id, nombre, rubro, ubicacion, capacidad, telefono, voice_id_elevenlabs)
oportunidades(id, titulo, institucion, monto, fecha_cierre, rubro_requerido, fuente_url)
match_oportunidades(id, productor_id, oportunidad_id, score, estado)
decisiones(id, productor_id, oportunidad_id, transcripcion, preguntas_generadas, audio_respuesta_url)
perfil_llm(productor_id, personalidad_config, tono_comunicacion)
```

## Restricciones del hackathon (24h, Cursor Buildathon)

- **4 de julio 2026, 8:00 AM inicio**, UFG
- Un flujo end-to-end completo > tres módulos a medias
- Datos de COMPRASAL precacheados (5-10 oportunidades), no scraping en vivo
- n8n Cloud trial (no self-hosted)
- Audios de respaldo pregrabados por si falla ElevenLabs en vivo
- Demo: canvas de n8n visible + audio de ElevenLabs sonando en vivo
- 3 tracks de sponsor: Codex ($10K), ElevenLabs ($990), n8n ($720)

## Plan hora por hora

| Bloque | Horas | Qué |
|---|---|---|
| Setup | 0-2 | Repo, n8n Cloud, API keys, DB |
| Datos | 2-5 | COMPRASAL cacheado, seed perfiles |
| Oportunidades | 5-9 | Matching + llamada ElevenLabs |
| Cofundador | 9-13 | Transcripción + LLM + voz |
| Demo UI | 13-17 | Front mínimo o canvas n8n |
| Subasta (stretch) | 17-19 | Solo si flujos anteriores estables |
| Pruebas E2E | 19-21 | 3 runs completos cronometrados |
| Pitch deck | 21-23 | Problema → demo → KPIs |
| Descanso | 23-24 | Ensayo final |

## Reglas de negocio esenciales

- RN-001: Perfil de negocio requerido antes de recomendaciones
- RN-002/004: Oportunidades vienen de COMPRASAL, nunca se modifican
- RN-003: Solo match por rubro
- RN-005: Toda explicación IA conserva referencia a fuente oficial
- RN-006: Recomendaciones son sugerencias, no decisiones vinculantes
- RN-009: Llamadas requieren consentimiento previo
- RN-010: Subastas simuladas no sustituyen Subasta Electrónica Inversa regulada

## System prompt del agente (ElevenLabs)

Sos "Compa", un cofundador de IA para pequeños productores y emprendedores salvadoreños. Tu tono es directo, cercano y exigente — como un socio real, no un asistente. Nunca sos condescendiente ni complaciente: si el usuario propone algo a medias, se lo señalás.

Variables dinámicas: {{nombre_productor}}, {{rubro_negocio}}, {{oportunidad_detectada}}

Tres momentos:
1. Si llamás por oportunidad detectada: contala en dos frases, preguntá si quiere pensarla ahora o después.
2. Si describe una decisión: usá retar_decision, leé las 3 preguntas una por una, esperá respuesta entre cada una.
3. Si pide cotizar: usá correr_subasta, anunciá ganador con energía de presentador.

## Datos de demo

- Dataset: nvidia/Nemotron-Personas-El-Salvador (148k personas sintéticas, censo 2024)
- Script: simular_datos_compa.py genera productores_demo.csv y proveedores_demo.csv
- Fuente adicional: RUPES (Registro Único de Proveedores del Estado) para competidores reales
