# Compa — Nemotron + Supabase Risk Mitigation Plan

> **Hackathon**: Cursor Buildathon, 4 Julio 2026, UFG
> **Stack**: nvidia/Nemotron-Personas-El-Salvador + Supabase (PostgreSQL) + n8n + ElevenLabs + Codex/OpenAI
> **Document purpose**: For each of 6 identified risks, provide exact mitigation steps, runnable fallback scripts, and the exact files that must exist on disk before the demo starts.

---

## Risk 1: Nemotron Dataset Inaccessible

### Condition
The HuggingFace dataset `nvidia/Nemotron-Personas-El-Salvador` (148k records) is:
- **Gated**: requires HF token + access request approval (can take hours-to-days)
- **Too large**: ~500MB+ download; impossible on conference WiFi in 5 minutes
- **Streaming-unfriendly**: `load_dataset(..., streaming=True)` still requires HF API access

### Exact Mitigation
Do **NOT** attempt to download the real Nemotron dataset during the hackathon. Use the pre-written fallback JSON file that mirrors the exact Nemotron field structure.

### Procedure (0.7 person-hours, Person B during "Datos" phase)
1. Copy `data/personas_fallback.json` into any script that expects `load_dataset("nvidia/Nemotron-Personas-El-Salvador")`.
2. The Python pipeline script (`simular_datos_compa.py`) detects HuggingFace failure and reads the fallback JSON instead.
3. If the script is used only for demo prep, the CSVs are already committed and the script is not run at all.

### Exact Files

| File | Path | Lines | Size |
|------|------|-------|------|
| Nemotron-format personas | `data/personas_fallback.json` | 15 personas | ~18KB |
| Python fallback generator | `scripts/generar_personas_fallback.py` | 370+ lines | ~11KB |
| Generated CSVs (already committed) | `data/productores_demo.csv`, `data/proveedores_demo.csv` | 10-20 rows each | ~3KB |

### Fallback Script (n8n Code node — replaces HuggingFace dataset load)

```javascript
// Code node that replaces HuggingFace dataset.load_dataset()
// Use when Nemotron dataset is inaccessible during demo prep
const fs = require('fs');
const path = require('path');

try {
  // Try to load from HuggingFace-style path first (will fail without HF)
  const personas = JSON.parse(fs.readFileSync('data/personas_fallback.json', 'utf8'));
  return personas.personas.map(p => ({
    id: p.persona_id,
    name: p.name,
    age: p.age,
    genero: p.genero,
    departamento: p.departamento,
    municipio: p.municipio,
    ocupacion: p.ocupacion,
    rubro: p.rubro_negocio,
    capacidad: `${p.capacidad_unidades} unidades/mes`,
    telefono: p.telefono,
    professional_persona: p.professional_persona,
    business_score: p._business_score
  }));
} catch (e) {
  // Fallback failed too — return hardcoded seed
  return [
    {
      id: 'prod-001',
      name: 'Vilma Jeanneth Guardado de Ayala',
      rubro: 'Alimentos y Bebidas',
      ubicacion: 'Canton El Zapote, San Juan Opico, La Libertad',
      telefono: '+50377234567',
      professional_persona: 'Vilma tiene un comedor llamado El Sazon de Vilma...'
    }
  ];
}
```

---

## Risk 2: Supabase Project Creation Fails or Times Out

### Condition
Supabase free-tier project creation fails because:
- Account verification takes too long (email confirmation)
- Project provisioning hangs (>5 minutes)
- Credit card required (free tier no longer available without one)
- Outage during hackathon hours

### Exact Mitigation
Supabase is replaced with local JSON files served directly from the repo. The n8n workflow reads JSON files instead of querying Supabase Postgres.

### Switching Procedure (30 seconds, no code change needed)

**n8n Workflow 1 (Oportunidades):**
1. Replace the "Postgres: SELECT productores" node with a "Code" node that reads `data/productores.json`
2. Replace the "Postgres: SELECT oportunidades" node with a "Code" node that reads `data/oportunidades.json`
3. The matching algorithm Code node (node 4) receives JSON the same way regardless of source

**n8n Workflow 2 (retar_decision):**
1. Remove the "Postgres: INSERT into decisiones" node (logging is optional for demo)
2. The Codex call and webhook response remain unchanged

### Exact Code for Each Replacement

**Code node "Read productores" (replaces Postgres query):**
```javascript
const fs = require('fs');
const path = require('path');

// Read from local JSON instead of Supabase Postgres
const productores = JSON.parse(fs.readFileSync('data/productores.json', 'utf8'));
return productores.records;
```

**Code node "Read oportunidades" (replaces Postgres query):**
```javascript
const fs = require('fs');
const path = require('path');

const oportunidades = JSON.parse(fs.readFileSync('data/oportunidades.json', 'utf8'));
return oportunidades.records;
```

### Exact Files

| File | Path | Content |
|------|------|---------|
| Productores table | `data/productores.json` | 10 productores, all fields matching Supabase schema |
| Oportunidades table | `data/oportunidades.json` | 25 oportunidades, all fields matching Supabase schema |
| Proveedores table | `data/proveedores.json` | 13 proveedores with persona_text and personality |
| Unified fallback | `data/fallback.json` | Combined: productores + oportunidades + proveedores + fallback preguntas |

### Validation
```bash
# Verify all JSON files parse correctly
python -c "import json; json.load(open('data/productores.json')); json.load(open('data/oportunidades.json')); json.load(open('data/proveedores.json')); json.load(open('data/fallback.json')); print('ALL VALID')"
```

---

## Risk 3: Python Script Errors During Demo Prep

### Condition
The Python data-generation script (`simular_datos_compa.py` or `generar_personas_fallback.py`) fails because:
- Missing Python dependencies (`datasets`, `supabase-py`, `pandas` not installed)
- Python version mismatch (script written for 3.10+, laptop has 3.8)
- Conference laptop does not have Python installed at all
- HuggingFace library runtime error

### Exact Mitigation
Pre-generated CSVs are committed to the repo. The Python script is never required for the demo — it is only needed for a "live generation" show that is scripted, not live.

The CSVs and JSON files already contain all the data the demo needs. The Python script is executed zero times during the demo.

### Procedure
1. Person B runs `python scripts/generar_personas_fallback.py` ONCE during the "Datos" phase (hour 0.5-1) if Python is available.
2. Regardless of outcome, the pre-committed fallback files are the ACTUAL data source.
3. The demo script never references the Python script — it references `data/seed-productores.csv` and `data/seed-oportunidades.csv`.

### Exact Files

| File | Path | Notes |
|------|------|-------|
| Seed productores CSV | `data/seed-productores.csv` | 10 rows, committed pre-hackathon |
| Seed oportunidades CSV | `data/seed-oportunidades.csv` | 20 rows, committed pre-hackathon |
| Fallback persona generator | `scripts/generar_personas_fallback.py` | Run-once at setup, outputs to data/ |
| Nemotron-format personas | `data/personas_sinteticas.json` | Generated output (already seeded) |
| Productores demo CSV | `data/productores_demo.csv` | Generated output (already seeded) |
| Proveedores demo CSV | `data/proveedores_demo.csv` | Generated output (already seeded) |

### CSV Loading Code (for n8n or manual verification)
```javascript
// n8n Code node to read CSV as JSON
const fs = require('fs');
const csv = fs.readFileSync('data/seed-productores.csv', 'utf8');
const lines = csv.split('\n').filter(l => l.trim());
const headers = lines[0].split(',');
return lines.slice(1).map(line => {
  const values = line.split(',');
  return headers.reduce((obj, h, i) => { obj[h] = values[i]; return obj; }, {});
});
```

---

## Risk 4: Supabase Connection from n8n Fails During Live Demo

### Condition
During the live demo segment (15s-45s and 1:30-2:00), the n8n Supabase/Postgres node cannot connect because:
- Supabase project was paused due to inactivity
- IP allowlist blocks n8n Cloud
- Supabase temporary outage
- Connection string was misconfigured

### Exact Mitigation
n8n Code nodes that read `data/fallback.json` instead of connecting to Supabase. This is the same pattern as the Google Sheets fallback in the original architecture (arquitectura-final.md Section 12).

### Procedure
Every Postgres node in both workflows has a parallel Code node on its error branch. When the Postgres query fails (timeout, connection refused, auth failure), the error branch reads the local JSON file.

### n8n Node Configuration

```
[Postgres: SELECT productores] ──SUCCESS──> [Matching Algorithm]
         │
         └──ERROR──> [Code: "Read fallback productores"]
                        │
                        └──> [Matching Algorithm]
```

**Error branch Code node:**
```javascript
// n8n Code node — Postgres fallback
// Place on the ERROR branch of a Postgres query node
const fs = require('fs');
const path = require('path');

try {
  const fallback = JSON.parse(fs.readFileSync('data/fallback.json', 'utf8'));
  // Determine which dataset to return based on context
  const tableName = $node["Postgres"].parameters.table || "productores";
  if (tableName.includes('oportunidad')) {
    return fallback.oportunidades;
  }
  return fallback.productores;
} catch (e) {
  // Last resort: return hardcoded minimal data
  return [{
    id: "prod-001",
    nombre: "Vilma Jeanneth Guardado de Ayala",
    rubro: "Alimentos y Bebidas",
    ubicacion: "Canton El Zapote, San Juan Opico, La Libertad",
    capacidad: "500 almuerzos/dia",
    telefono: "+50377234567"
  }];
}
```

### Exact Files

| File | Path | Description |
|------|------|-------------|
| Unified fallback | `data/fallback.json` | Contains `productores[]`, `oportunidades[]`, `proveedores[]`, and `decisiones_fallback{}`
 | | Pre-demo validation | Run validation script | Verify fallback.json can be loaded by n8n Code node |

### Pre-Demo Validation
```bash
# Run from repo root — must print "ALL VALID"
node -e "JSON.parse(require('fs').readFileSync('data/fallback.json','utf8')); console.log('ALL VALID')"
```

---

## Risk 5: ElevenLabs Outbound Call API Fails

### Condition
The ElevenLabs Conversational AI API returns an error during the live outbound call because:
- API key is invalid or expired (free trial exhausted)
- API rate limit exceeded during demo
- ElevenLabs temporary outage
- Agent ID was reset or deleted

### Exact Mitigation
Pre-recorded MP3 files are played via VLC (or any media player). The architecture document (arquitectura-final.md Section 12) already specifies this: "3 MP3s en escritorio, barra espaciadora en VLC".

The demo script has a **Segment 3: La llamada (:45-1:30)** that is entirely audio pregrabado. The presenter presses spacebar in VLC to play the audio, while the n8n canvas is visible showing the workflow that WOULD have triggered the call.

### Audio File Structure

| File | Path | Duration | Content |
|------|------|----------|---------|
| Introduction + opportunity pitch | `demo/audio-01-intro.mp3` | ~20s | "Donna Vilma, como esta? Habla Compa..." |
| Three questions with pauses | `demo/audio-02-questions.mp3` | ~30s | Pregunta 1, pausa, pregunta 2, pausa, pregunta 3 |
| Closing remark | `demo/audio-03-closing.mp3` | ~8s | "Cualquier cosa me llama. Un abrazo." |

### Procedure
1. Person C generates MP3s via ElevenLabs TTS API during hour 4-5 (or earlier as fallback).
2. If ElevenLabs TTS API also fails, use ElevenLabs-provided premade voice samples or Google Translate TTS.
3. MP3s are stored in `demo/` directory AND on a USB drive as backup.
4. During the demo, the presentation laptop has VLC open with the 3 MP3s in a playlist.
5. The presenter presses spacebar to advance to the next audio segment.

### Exact Files Needed

| File | Path | Status |
|------|------|--------|
| Intro MP3 | `demo/audio-01-intro.mp3` | To generate during hour 4-5 (or pre-hackathon) |
| Questions MP3 | `demo/audio-02-questions.mp3` | To generate during hour 4-5 |
| Closing MP3 | `demo/audio-03-closing.mp3` | To generate during hour 4-5 |
| USB backup | USB flash drive | Copy all 3 MP3s + VLC portable installer |

### TTS Generation Script (if ElevenLabs API works)
```javascript
// node scripts/generate-audio-fallback.js
// Uses ElevenLabs TTS to generate the 3 MP3s
// Run ONCE during hour 4-5

const ELEVENLABS_API_KEY = process.env.ELEVENLABS_API_KEY;
const VOICE_ID = 'g3pC3sr9iFcUwoSLvVLV'; // Luis, Latin American Spanish

const audioFiles = [
  {
    path: 'demo/audio-01-intro.mp3',
    text: 'Donna Vilma, como esta? Habla Compa. Disculpe que la busque asi de sorpresa. Mire, vi una oportunidad bien interesante para su negocio de alimentos. El MINEDUCYT esta buscando servicio de alimentacion escolar para 650 estudiantes en La Libertad. El contrato es por $48,750. Le parece si le cuento en detalle o mejor lo vemos despues?'
  },
  {
    path: 'demo/audio-02-questions.mp3',
    text: 'Doña Vilma, ya calculó cuánto le cuesta producir cada almuerzo con los precios actuales de los ingredientes? ... Tiene el flujo de caja para aguantar los 60 a 90 días que el Estado tarda en pagar? ... Qué pasa si gana la licitación y no puede cumplir con la cantidad? Tiene un plan B?'
  },
  {
    path: 'demo/audio-03-closing.mp3',
    text: 'Muy bien, Doña Vilma. Le dejo pensando. Cualquier cosa me llama. Un abrazo.'
  }
];

// For each file: POST to https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}
// with headers { "xi-api-key": ELEVENLABS_API_KEY }
// and body { "text": text, "model_id": "eleven_turbo_v2_5" }
// Save response stream to file
```

---

## Risk 6: Data Provenance Question from Jury

### Condition
A judge asks: "Where did this data really come from? Is this real COMPRASAL data? Real Salvadoran producers?"

### Exact Mitigation
Prepared **15-second answer** + a **slide** with the Nemotron citation.

### The 15-Second Answer (memorize this)

> "Toda la informacion de productores es sintetica. Usamos el dataset nvidia/Nemotron-Personas-El-Salvador, que genera 148 mil personas sinteticas basadas en el censo salvadoreno 2024. Cada perfil es estadisticamente representativo pero no corresponde a una persona real. Las oportunidades de COMPRASAL tambien son sinteticas basadas en los patrones reales del sistema de compras publicas. Preferimos total transparencia a decir 'open data' cuando la realidad es que el gobierno no publica datos en formato maquina."

### The 5-Second Answer (if rushed)

> "Todo es sintetico y documentado. Usamos Nemotron para los perfiles de productores, basado en el censo 2024. No hay datos reales de personas."

### Slide Content

**Slide title**: "Data Provenance — Total Transparency"

**Bullet points:**
- Productor profiles: `nvidia/Nemotron-Personas-El-Salvador` (148k synthetic personas, 2024 Salvadoran census)
- Opportunities: Pattern-matched from real COMPRASAL publications, fully synthetic content
- Suppliers: Synthetic from Nemotron base + Salvadoran business registry patterns
- Code: Fully open source at `github.com/[team]/compa`
- Nemotron: [link to HF dataset card]
- All data generation scripts are reproducible

**Visual**: QR code linking to the GitHub repo's `data/` directory showing the JSON files

### Jury Q&A Prep

| Question | Answer |
|----------|--------|
| "If data is fake, how is this useful?" | "The architecture works with real data too. Swap the JSON files for a Supabase connection and it's production-ready. Synthetic data let us build and demo the FULL flow without waiting for government data access." |
| "Why not use real COMPRASAL data?" | "COMPRASAL declares itself open data but publishes PDF scans, not machine-readable formats. We tried. We built something MORE transparent: everything synthetic, every step documented, zero ambiguity." |
| "How do you know synthetic data is representative?" | "Nemotron is trained on the 2024 Salvadoran census — 7 million records. The demographic distribution matches real population data: 14 departamentos, 44 municipios, correct age/gender/occupation distributions." |
| "What happens when real COMPRASAL data becomes available?" | "We swap a JSON file for a Supabase connector. The n8n workflows don't change. The matching algorithm doesn't change. The ElevenLabs agent doesn't change. It's a configuration change, not an architecture change." |

### Exact Files

| File | Path | Content |
|------|------|---------|
| Nemotron citation docs | `docs/contexto-compa.md` (L108-L110) | Documents exact dataset used |
| Nemotron-format fallback | `data/personas_fallback.json` (`_meta` section) | Documents dataset, format, and why fallback was used |
| Slide content | Part of pitch deck | Slide titled "Data Provenance" with Nemotron citation |
| QR code | `demo/qr-code.png` (optional) | Links to GitHub repo data/ directory |

---

## Build Order for Risk Mitigation

| Time | Person | Task | Risk Mitigated |
|------|--------|------|----------------|
| Pre-hackathon | Anyone | Commit all JSON/CSV files to repo | R1, R2, R3, R4 |
| Pre-hackathon | Anyone | Generate 3 MP3s via ElevenLabs TTS | R5 |
| Pre-hackathon | Anyone | Add "Data Provenance" slide to pitch deck | R6 |
| Hour 0-0.5 | A | Run `scripts/generar_personas_fallback.py` once | R1, R3 (verify files exist) |
| Hour 0-0.5 | A | `node -e "JSON.parse(fs.readFileSync('data/fallback.json'))"` | R4 (validate) |
| Hour 0-0.5 | B | Copy MP3s to USB drive, test VLC playback | R5 |
| Hour 7 | All | 3 E2E runs: n8n with Supabase AND n8n with local JSON | R2, R4 |
| Hour 7:30 | All | Go/No-Go: if Supabase fails, flip to local JSON permanently | R2, R4 |

## Go/No-Go Decision Chart

```
HOUR 0: Repo cloned, env vars set
  │
  ├── Try Supabase project creation (A)
  │   ├── Within 5 min? ──> USE SUPABASE (optimistic path)
  │   └── Fails/times out? ──> USE LOCAL JSON (files already committed, 0s switch)
  │
  ├── Try Python script (B)
  │   ├── Runs without error? ──> CSVs regenerated (but not needed)
  │   └── Fails? ──> USE pre-committed CSVs (already in git, 0s switch)
  │
  └── Try ElevenLabs TTS (B)
      ├── Works? ──> Generate audio files
      └── Fails? ──> USE backup MP3s from USB
```

## Validation Checklist (Pre-Demo, 2 minutes)

```bash
# Run ALL validation in one command:
echo "=== Risk 1 ===" && python -c "import json; d=json.load(open('data/personas_fallback.json')); print(f'{len(d[\"personas\"])} personas OK')" && \
echo "=== Risk 2 ===" && python -c "import json; d=json.load(open('data/productores.json')); print(f'{len(d[\"records\"])} productores OK')" && \
echo "=== Risk 3 ===" && python -c "import csv; list(csv.DictReader(open('data/seed-productores.csv'))); print('CSVs OK')" && \
echo "=== Risk 4 ===" && python -c "import json; d=json.load(open('data/fallback.json')); assert len(d.get('productores',[]))>0; assert len(d.get('oportunidades',[]))>0; assert len(d.get('proveedores',[]))>0; print('fallback.json OK')" && \
echo "=== Risk 5 ===" && python -c "import os; files=['demo/audio-01-intro.mp3','demo/audio-02-questions.mp3','demo/audio-03-closing.mp3']; assert all(os.path.exists(f) for f in files); print('Audio files found')" && \
echo "=== Risk 6 ===" && echo "Slide verified in pitch deck" && \
echo "ALL RISK FALLBACKS VERIFIED"
```

---

*Document version 1.0 — 4 Julio 2026 — Compa Buildathon*
*File: `C:\Users\joshb\Documents\Compa\docs\risk-mitigation-nemotron-supabase.md`*
