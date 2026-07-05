# Compa — Audit Report (30 Reviewers)

**29/30 agentes completados. 2.67M tokens. ~31 min.**
**Fecha: 4 Julio 2026**

---

## Overall Health

| Dimensión | Estado |
|---|---|
| **Schema** | RED — falta tabla `match_oportunidades`, `decisiones` le faltan 4 columnas |
| **Workflows** | RED — INSERT a decisiones fallará en runtime por column mismatch |
| **Agent Config** | GREEN — bien documentado, sin issues |
| **Scripts** | YELLOW — bien estructurados pero datos inconsistentes entre SQL/JSON/CSV |
| **Architecture** | YELLOW — docs detallados pero schema drifted del spec |
| **Risk** | RED — 2 productores reciben 0 matches, fallback UUID hardcodeado rompe FK |
| **Narrative** | YELLOW — historia core funciona para Vilma pero claims factuales necesitan verificación |

---

## 10 Critical Issues (must fix before demo)

### 1. `match_oportunidades` table missing
`supabase-schema.sql`. El spec la requiere (COMPA-DEFINITIVE-IMPLEMENTATION.md), el workflow n8n espera persistir matches. No existe en el schema.

### 2. `decisiones` missing 4 columns
`supabase-schema.sql:63-70`. El n8n workflow espera: `oportunidad_id`, `conversation_id`, `respuesta_raw`, `es_fallback`. El schema real solo tiene 5 columnas. El INSERT fallará en runtime.

### 3. n8n `productor_id` mapped to name string, not UUID
`n8n-workflow-especificaciones.md:514`. Mapea `{{ $json.nombre_productor }}` ("Vilma Jeanneth...") a una columna UUID. FK violation garantizada. Mismo problema en `oportunidad_id:515` que usa `conversation_id`.

### 4. Ana Beatriz Cruz de Lemus: 0 matches
`supabase-schema.sql:93`. Rubro "Servicios Generales". Ninguna oportunidad en SQL ni JSON usa ese rubro. 1 de 5 productores del demo no funciona.

### 5. María Susana Mejía Argueta: 0 matches
`supabase-schema.sql:103`. Rubro "Comercio y Distribución". Cero resultados en `matching_oportunidades()`. El fuzzy fallback tampoco la rescata (SPLIT_PART produce "Comercio" que no existe en ningún rubro_requerido).

### 6. SQL 41 oportunidades vs JSON 31
Faltan 10 oportunidades en `data/oportunidades.json`: Transporte, Publicidad, Mensajería, Deportivos, Medios, Educativos, Limpieza + extras de Tecnología y Alimentos.

### 7. Accent mismatch SQL vs JSON
JSON usa strings sin acentos ("Tecnologia", "Papeleria", "Medicos"), SQL usa acentos ("Tecnología", "Papelería", "Médicos"). PostgreSQL `=` es accent-sensitive. Matching entre fuentes roto.

### 8. Header dice "51 REALES", solo hay 50 INSERTs
`supabase-schema.sql:46`. Falta un proveedor o el comentario está mal.

### 9. 15-23 catalog providers missing from SQL
Faltan en SQL: GRUPO ASINET, SCREENCHECK, SOLUTECNO, GEOSIS, NEXT GENESIS, DATUM, DOCUMENTOS INTELIGENTES, INTRACON, HOTELES, Baltazar Gómez, Bryan Fuentes, y más. Tres rubros del catálogo sin proveedores en SQL: Seguridad Documental, Servicios Deportivos, Servicios de Catering.

### 10. 3 provider pairs duplicated with inconsistent rubro
- LANDOS + LANDOS (Encuadernados) — mismo rubro, distinto description
- SUPLIDORES DIVERSOS + SUPLIDORES DIVERSOS (Médico) — mismo description, DISTINTO rubro
- CONSULTORIA MEDIO AMBIENTE + CONSULTORIA MEDIO AMBIENTE (Ambiental) — mismo description, DISTINTO rubro

---

## Important Issues (should fix if time)

1. **CHECK constraints ausentes** — DUI/NIT/telefono regex del spec no están en el schema real
2. **Dead code en matching function** — rama `ELSE 40` inalcanzable por el WHERE clause
3. **Sin índice en `decisiones.productor_id`** — sequential scans en todos los lookups
4. **Sin LIMIT en matching function** — puede retornar cientos de rows
5. **16 de 88 proveedores (18%) "Sin clasificar"** — todos del dataset 2019
6. **Espacio líder en título** — `' Servicio de Catering...'` en `supabase-schema.sql:114`
7. **Fuzzy matching impreciso** — `SPLIT_PART('Servicios de Mantenimiento', ' ', 1)` = "Servicios" matchea TODO
8. **Sin seed data para `decisiones`** — el demo no puede mostrar el flow de AI questioning
9. **`documentos_generados.plantilla_id` sin ON DELETE** — defaults a NO ACTION
10. **Stale count en comentario** — `supabase-schema.sql:107` dice "25" pero son 41 rows
11. **n8n Merge node "Wait for Both"** incorrecto para triggers independientes (Manual + Cron)
12. **Supabase Storage node no existe en n8n** — requiere HTTP Request workaround
13. **`matching_oportunidades` omite `unspsc_code` y `url_fuente`** en RETURN TABLE
14. **Sin composite index `(rubro_requerido, monto DESC)`** para optimizar la matching function

---

## Knowledge Base Critical Gaps

1. **4 de 8 PDFs son scanned images** — sin texto extraíble, invisibles para ElevenLabs RAG
2. **Tamaño real ~24.3MB** — excede el límite de 20MB del plan estándar
3. **Faltan documentos críticos**: Reglamento LCP, Lineamiento Baja Cuantía, Comparación de Precios
4. **Estimaciones de tamaño en el config off por 5-12x**

---

## Python Script Issues

1. **`simular_datos_compa.py`**: rubro names inconsistentes con SQL schema (rompe matching)
2. **`generar_personas_fallback.py`**: nombre duplicado, función helper definida pero nunca llamada, pesos calculados y descartados
3. **`generador_oportunidades.py`**: sin random seed fijo (no reproducible), varios UNSPSC codes incorrectos, acentos ausentes
4. **Cross-script**: los dos generadores de personas escriben al mismo filename con formatos incompatibles

---

## ElevenLabs Agent Gaps

1. **Sin mode-transition protocol** — ¿qué pasa si el usuario salta de Oportunidades → Legal → Documento?
2. **RAG ambiguity** — el agente no sabe CUÁNDO buscar en Knowledge Base vs responder directo
3. **Tool `generar_documento`**: productor_id required pero el agente no tiene forma de obtener el UUID (no está en dynamic_variables, no hay lookup tool)
4. **Timeout 25s puede ser insuficiente** para documento generation (DB queries + DOCX merge + storage upload)
5. **Sin fallback para documento type inexistente** — el agente no sabe qué decir si el usuario pide un tipo no en plantillas

---

## Conversation Edge Cases (no cubiertos)

1. Silencio del usuario — sin protocolo
2. Usuario enojado/confundido — sin de-escalation
3. "Pasame con una persona real" — sin human handoff
4. Usuario habla inglés/spanglish — sin handler
5. Usuario pide firmar documento — sin respuesta programada
6. Usuario cuelga mid-document-generation — ¿qué pasa con el documento incompleto?
7. Bad audio/static — sin protocolo de repetición

---

## Demo Feasibility Issues

1. **Contradicción de tiempos**: COMPA-DEFINITIVE-IMPLEMENTATION.md dice 3.5h build, arquitectura-final.md asigna 8h
2. **n8n workflow build estimado en 30 min** — irreal para workflows de 11-15 nodos
3. **ElevenLabs agent config en 30 min** — no alcanza para KB upload + tool config + voice tuning
4. **Directorio `demo/` vacío** — no hay MP3s, no hay pitch deck, no hay QR
5. **Directorio `n8n-exports/` sin JSONs importables** — solo markdown specs
6. **3-minute demo script incompleto** — solo estructura de segmentos, falta el texto narrativo completo
7. **Live n8n + pre-recorded audio sync** — no ensayado, alto riesgo de desincronización en vivo

---

## Track Strategy Assessment

| Track | Fortaleza | Debilidad |
|---|---|---|
| **Codex** ($10K) | `reasoning_trace` visible, contexto legal salvadoreño en prompt | gpt-4o-mini no es "Codex" brand, ¿lo aceptan los jueces? |
| **ElevenLabs** ($990) | Tools, RAG, dynamic variables, system prompt sólido | Demo usa MP3s pregrabados, no llamadas live — debilita la impresión |
| **n8n** ($720) | 2 workflows con error branches visibles en canvas | Subasta loop cortado (era el showcase n8n), Storage node no existe |

---

## What Is Working Well

1. **88+ proveedores reales** del registro público — el asset más fuerte del proyecto. Esto es datos que NADIE más tiene en el hackathon.
2. **Lógica del matching function** sólida para el caso común (Vilma = 5 matches exactos en Alimentos)
3. **Formato teléfono/DUI/NIT** consistente en los 15 productores — sin errores de formato
4. **Módulo legal** bien concebido: 6 plantillas con URLs DINAC reales, `campos_requeridos` JSONB, flujo de validación pensado
5. **Cobertura de índices** buena para query patterns principales
6. **Workflows n8n** bien documentados con fallback mechanisms y error branches
7. **RLS policies** correctamente estructuradas en todas las tablas
8. **System prompt** con voseo correcto, disclaimers legales claros, anti-hallucination rules explícitas
9. **Transparencia**: 3 fuentes del registro público (2019, jul-sep 2025, ene-mar 2026) — cobertura temporal legítima
10. **21 rubros** cubriendo el espectro real de compras públicas salvadoreñas

---

## Demo Readiness: 40%

**Funcionaría en demo:**
- Matching de Vilma (Alimentos y Bebidas → 5 oportunidades)
- Directorio de proveedores (88 reales)
- Listado de plantillas legales (6 tipos)
- Workflow 1 ejecutándose en canvas (hasta el HTTP Request a ElevenLabs)

**FALLARÍA en demo:**
- Pipeline AI questioning → persistencia (INSERT a decisiones falla)
- Match persistence (tabla match_oportunidades no existe)
- Ana Beatriz y María Susana (0 matches — 2 de 5 productores rotos)
- Document generation sin plantillas DOCX reales ni Storage bucket

**Para llegar a 85%:** ~3 horas de un dev aplicando los 10 critical issues (todos son DDL SQL o correcciones de mapeo, no rediseños).

---

## Open Questions for the Team

1. ¿Se crea `match_oportunidades` o fue omitida a propósito?
2. ¿Schema de `decisiones` debe matchear n8n workflow o actualizamos el n8n?
3. ¿41 (SQL) o 31 (JSON) oportunidades como fuente de verdad?
4. ¿"Servicios Generales" intencional como edge case? ¿O cambiamos el rubro de Ana Beatriz?
5. ¿"Comercio y Distribución" — agregamos oportunidades o reconsideramos?
6. ¿Unificamos `productores` y `proveedores` en una sola tabla?
7. ¿"Servicios de Limpieza" vs "Suministros de Limpieza" — son distintos?
8. ¿Los natural-person suppliers en productores deben también estar en proveedores?
9. ¿Merge node "Wait for Both" es correcto para Manual + Cron triggers independientes?
10. ¿MP3s pregrabados o intentamos llamada live de ElevenLabs?

---

*Informe generado por 30 agentes revisores especializados.*
*Archivo: `C:\Users\joshb\Documents\Compa\docs\audit-report-30-agents.md`*
