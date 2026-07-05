# Fase 3 - n8n y ElevenLabs

## Entregables

- `n8n-exports/workflow-oportunidades-elevenlabs.json`: workflow importable para leer Supabase, tomar el match principal de Vilma y llamar ElevenLabs con `dynamic_variables`.
- `n8n-exports/workflow-retar-decision.json`: workflow importable para el tool `retar_decision`, con validacion de UUIDs, OpenAI, fallback e INSERT en `decisiones`.
- `n8n-exports/elevenlabs-tool-retar-decision.json`: definicion del tool para copiar al dashboard de ElevenLabs.
- `demo/payload-retar-decision-vilma.mock.json`: payload local con UUIDs validos para probar validacion sin tocar Supabase.
- `scripts/test_phase3_contract.py`: prueba estatica del contrato.

## Variables requeridas en n8n

- `ELEVENLABS_API_KEY`
- `ELEVENLABS_AGENT_ID`
- `OPENAI_API_KEY`
- `COMPA_WEBHOOK_SECRET` (opcional; default `whsec_compa_buildathon_2026`)

## Credenciales requeridas en n8n

Crear una credential tipo Postgres llamada `Supabase Postgres` y asignarla a los dos nodos Postgres despues de importar los workflows.

## Contrato de payload para `retar_decision`

El body debe ser plano, no anidado, para evitar drift:

```json
{
  "decision_descrita": "Me interesa participar...",
  "productor_id": "<uuid-real-supabase>",
  "oportunidad_id": "<uuid-real-supabase>",
  "conversation_id": "<id-elevenlabs>",
  "nombre_productor": "Vilma Jeanneth Guardado de Ayala",
  "rubro_negocio": "Alimentos y Bebidas",
  "capacidad_productor": "500 almuerzos/dia",
  "oportunidad_titulo": "Servicio de Alimentacion Escolar - Distrito 04-25",
  "oportunidad_institucion": "MINEDUCYT",
  "oportunidad_monto": 48750,
  "oportunidad_cierre": "2026-07-18"
}
```

`productor_id` y `oportunidad_id` deben venir de Supabase como UUID reales. Los IDs locales `prod-001` y `opp-001` solo son fallback JSON.

## Prueba local

```powershell
C:\Users\isabe\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe Compa\scripts\test_phase3_contract.py
```

Salida esperada:

```text
phase3 contract ok
```

## Prueba en n8n

1. Importar ambos JSON.
2. Asignar credential `Supabase Postgres` a los nodos Postgres.
3. Definir las variables de entorno.
4. Ejecutar `COMPA - Fase 3 - Oportunidades a ElevenLabs` manualmente.
5. En ElevenLabs, configurar el tool con `elevenlabs-tool-retar-decision.json`.
6. Probar `POST /retar-decision` con un payload real donde `productor_id` y `oportunidad_id` hayan salido de Supabase.

## Criterio de listo

La Fase 3 queda lista cuando:

- n8n importa los dos workflows sin reconstruirlos desde Markdown.
- El payload outbound a ElevenLabs incluye `dynamic_variables.productor_id` y `dynamic_variables.oportunidad_id`.
- El tool `retar_decision` exige UUIDs reales.
- El workflow guarda la respuesta en `decisiones` y responde 200 con tres preguntas, aunque OpenAI falle y se use fallback.
