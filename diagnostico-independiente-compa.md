# COMPA - Diagnostico Independiente del Proyecto

**Fecha:** 4 de julio de 2026  
**Autor:** Codex  
**Alcance:** Revision estatica del repositorio local, schema SQL, documentacion, specs n8n, datasets y assets de demo.  
**Fuente de verdad usada:** archivos ejecutables y datos presentes en `C:\Users\isabe\Documents\COMPA`, no promesas descritas en documentos de arquitectura.

---

## 1. Veredicto Ejecutivo

Mi diagnostico es que COMPA esta en estado de **prototipo avanzado pero no demo end-to-end confiable**.

La idea central es fuerte: un agente de voz que detecta oportunidades de compras publicas, contacta productores, reta decisiones de negocio con preguntas generadas por IA y deja trazabilidad. Tambien hay buenos activos: datos de proveedores reales, narrativa de transparencia, schema base en Supabase, scripts de generacion y documentacion amplia.

El problema principal no es falta de vision ni falta de codigo. El problema es **drift de integracion**: el schema real, los workflows documentados, los datasets, el modulo legal y los assets esperados para demo no estan alineados entre si.

**Readiness estimado:** 40% para demo integrada.  
**Readiness posible en pocas horas:** 75-85% si se recorta alcance y se arreglan los puntos criticos de schema, datos y demo.  
**Recomendacion:** presentar una demo controlada con una ruta minima funcionando, no prometer todos los modulos como produccion.

---

## 2. Estado por Componente

| Componente | Estado | Diagnostico |
|---|---:|---|
| Concepto de producto | Verde | Problema claro, demo con potencial y buena narrativa. |
| Datos de proveedores | Verde/Amarillo | Hay 88 proveedores en SQL; activo fuerte, pero catalogos y SQL no coinciden completamente. |
| Supabase schema | Rojo | Tablas base existen, pero faltan columnas esperadas por n8n y falta `match_oportunidades`. |
| Workflow n8n | Rojo | Solo hay specs Markdown, no JSON importable; el INSERT de decisiones no calza con el schema real. |
| ElevenLabs agent | Amarillo/Rojo | Prompt y herramientas estan pensadas, pero falta una ruta clara para obtener `productor_id`. |
| Modulo legal DINAC | Amarillo/Rojo | Buen diseno conceptual; document generation no esta implementado end-to-end. |
| Scripts Python | Amarillo | Compilan, pero producen rubros/datasets no alineados con el SQL. |
| Datos locales JSON/CSV | Rojo | Multiples fuentes de verdad con conteos distintos. |
| Demo assets | Rojo | `demo/` existe pero esta vacio; no hay MP3s, deck ni QR. |
| Documentacion | Amarillo | Muy completa, pero describe capacidades que no existen en archivos ejecutables actuales. |

---

## 3. Evidencia Verificada

### 3.1 Conteos reales encontrados

En `Compa/supabase-schema.sql`:

| Tabla / seed | Conteo detectado |
|---|---:|
| `productores` | 15 |
| `oportunidades` | 41 |
| `proveedores` | 88 |
| `plantillas_documentos` | 6 |

En `Compa/data`:

| Archivo | Conteo / estructura |
|---|---|
| `fallback.json` | 5 productores, 20 oportunidades, 10 proveedores |
| `oportunidades.json` | 31 oportunidades |
| `personas_fallback.json` | 15 personas |
| `personas_sinteticas.json` | 30 personas |
| `productores.json` | 10 records |
| `proveedores.json` | 13 records |
| `oportunidades.csv` | 25 filas |
| `seed-oportunidades.csv` | 20 filas |
| `seed-productores.csv` | 10 filas |
| `productores_demo.csv` | 15 filas |
| `proveedores_demo.csv` | 15 filas |

Esto confirma que no existe una unica fuente de verdad para demo.

### 3.2 Schema real de `decisiones`

El schema actual define:

```sql
CREATE TABLE IF NOT EXISTS decisiones (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    productor_id      UUID REFERENCES productores(id) ON DELETE CASCADE,
    decision_descrita TEXT NOT NULL,
    preguntas_json    JSONB,
    reasoning_trace   TEXT,
    created_at        TIMESTAMPTZ DEFAULT now()
);
```

Pero el workflow n8n documentado intenta insertar:

```text
productor_id,
oportunidad_id,
decision_descrita,
conversation_id,
preguntas_generadas,
reasoning_trace,
respuesta_raw,
es_fallback,
creado_en
```

Ese INSERT fallaria porque la tabla real no contiene la mayoria de esas columnas.

### 3.3 `productor_id` esta mal mapeado

El workflow documentado mapea:

```text
productor_id = {{ $json.nombre_productor }}
oportunidad_id = {{ $json.conversation_id }}
```

Esto no es compatible con un campo `UUID REFERENCES productores(id)`. Si se ejecuta contra el schema real, debe fallar por tipo invalido o FK invalida.

### 3.4 Falta `match_oportunidades`

El contexto original menciona:

```text
match_oportunidades(id, productor_id, oportunidad_id, score, estado)
```

Pero `supabase-schema.sql` no crea esa tabla. La funcion `matching_oportunidades()` calcula matches, pero no persiste resultados.

### 3.5 n8n no tiene exports reales

El directorio `Compa/n8n-exports` contiene:

```text
n8n-workflow-especificaciones.md
workflow-generar-documento-dinac.md
```

No hay archivos `.json` importables en n8n. Esto baja la readiness real porque construir workflows manualmente desde Markdown toma tiempo y es propenso a errores.

### 3.6 `demo/` esta vacio

El directorio `Compa/demo` existe, pero no contiene:

```text
audio-01-intro.mp3
audio-02-questions.mp3
audio-03-closing.mp3
pitch-deck.pdf
qr-code.png
```

Los documentos de riesgo y arquitectura dependen de esos assets, pero no estan presentes.

### 3.7 Legal KB supera ampliamente 20 MB si se sube completa

La carpeta `Compa/DocumentacionLegal` contiene aproximadamente:

| Tipo | Conteo | Tamano |
|---|---:|---:|
| PDF | 42 | 154.7 MB |
| DOCX | 16 | 2.51 MB |
| Total documentos | - | 157.22 MB |

Si el plan de ElevenLabs o la configuracion de KB tiene limites bajos, no se puede subir todo sin curar/seleccionar documentos.

---

## 4. Donde Estoy de Acuerdo con el Reporte Existente

Estoy de acuerdo con el diagnostico central:

1. **El sistema no esta listo para una demo end-to-end real.**
2. **El schema y el workflow `retar_decision` estan desalineados.**
3. **Falta persistencia de matches en `match_oportunidades`.**
4. **Los datasets SQL/JSON/CSV estan inconsistentes.**
5. **La ruta de documentos DINAC no esta cerrada.**
6. **El directorio de demo esta incompleto.**
7. **La demo depende demasiado de assets y configuraciones aun no materializadas.**

Tambien comparto la idea de que el proyecto tiene activos fuertes:

1. La narrativa de transparencia es buena.
2. Los proveedores reales son el mejor diferencial.
3. La experiencia de voz puede ser memorable si se muestra bien.
4. `reasoning_trace` es una buena pieza para explicar valor de IA, no solo output.

---

## 5. Donde No Estoy de Acuerdo o Matizaria el Reporte

### 5.1 Conteos de proveedores

El reporte dice que el header habla de 51 proveedores pero solo hay 50 INSERTs. En el SQL actual detecte **88 proveedores**. Puede que el reporte haya auditado una version anterior o haya contado solo una seccion.

Mi conclusion: el comentario del archivo sigue desactualizado, pero el problema no es que falten proveedores en general; el problema es que **el catalogo de proveedores y el SQL no coinciden completamente**.

### 5.2 Indice en `decisiones.productor_id`

El reporte afirma que falta un indice en `decisiones.productor_id`. En el SQL real tampoco encontre ese indice en la zona del schema base, asi que el riesgo aplica. Sin embargo, la documentacion definitiva si lo menciona como si existiera. Este es otro caso de drift: docs prometen mas que el SQL real.

### 5.3 `matching_oportunidades` y campos retornados

El reporte dice que la funcion omite `unspsc_code` y `url_fuente`. Eso es cierto para el SQL actual: la funcion retorna `tipo_contratacion`, pero no esos dos campos. La documentacion definitiva, en cambio, muestra una version mas completa. Fuente de verdad: el SQL actual.

### 5.4 Productores con cero matches

El reporte afirma que Ana Beatriz y Maria Susana quedan con cero matches. Esto parece correcto para la funcion SQL si sus rubros no aparecen en oportunidades. Sin embargo, el SQL actual ya incluye proveedores de `Comercio y Distribucion`, no oportunidades. El problema real es: **hay rubros con productores/proveedores, pero no con oportunidades equivalentes**.

---

## 6. Riesgos Criticos para Demo

### Riesgo 1: Falla el insert de decisiones

**Impacto:** alto.  
**Probabilidad:** alta.  
**Causa:** columnas n8n no existen en SQL y IDs mal mapeados.  
**Solucion:** alinear schema o workflow. Recomiendo cambiar schema para soportar trazabilidad completa.

### Riesgo 2: No hay workflow importable

**Impacto:** alto.  
**Probabilidad:** alta si se intenta montar n8n desde cero.  
**Causa:** solo hay specs Markdown.  
**Solucion:** crear JSON export real o recortar demo a un webhook minimo.

### Riesgo 3: Demo de voz depende de MP3s inexistentes

**Impacto:** alto.  
**Probabilidad:** alta.  
**Causa:** `demo/` vacio.  
**Solucion:** generar 3 audios o cambiar guion para usar texto/simulacion.

### Riesgo 4: El modulo legal no puede completar `generar_documento`

**Impacto:** medio/alto.  
**Probabilidad:** alta.  
**Causa:** agente exige `productor_id`, plantillas estan en storage teorico, generacion DOCX es simulada.  
**Solucion:** declararlo como "preview" o quitarlo de la demo principal.

### Riesgo 5: Datasets inconsistentes producen resultados distintos segun fuente

**Impacto:** medio/alto.  
**Probabilidad:** alta.  
**Causa:** SQL, JSON y CSV tienen conteos/rubros diferentes.  
**Solucion:** declarar SQL como source of truth y regenerar JSON/CSV desde ahi.

---

## 7. Plan de Recuperacion Prioritario

### Fase 1 - Demo minima estable

Objetivo: que una sola ruta funcione de inicio a fin.

1. Elegir un productor principal: Vilma.
2. Elegir SQL como fuente de verdad.
3. Ajustar `decisiones` para aceptar los campos que n8n necesita:
   - `oportunidad_id`
   - `conversation_id`
   - `preguntas_generadas` o renombrar a `preguntas_json`
   - `respuesta_raw`
   - `es_fallback`
   - `creado_en` o usar `created_at`
4. Corregir n8n para pasar UUID real de productor y oportunidad.
5. Crear `match_oportunidades`.
6. Generar assets basicos de `demo/`.

### Fase 2 - Consistencia de datos

1. Exportar desde SQL a:
   - `data/oportunidades.json`
   - `data/fallback.json`
   - `data/seed-oportunidades.csv`
2. Normalizar rubros con una lista cerrada.
3. Evitar versiones con y sin acentos para el mismo rubro.
4. Agregar oportunidades para rubros demo sin matches.

### Fase 3 - n8n y ElevenLabs

1. Crear workflow JSON importable para oportunidades.
2. Crear workflow JSON importable para `retar_decision`.
3. Validar payload exacto de ElevenLabs outbound.
4. Pasar `productor_id` y `oportunidad_id` como dynamic variables.
5. Probar webhook con payload realista.

### Fase 4 - Legal como modulo secundario

1. No incluir document generation en la demo principal salvo que este probado.
2. Curar KB legal: seleccionar pocos documentos esenciales, no subir 157 MB completos.
3. Definir mecanismo para resolver `productor_id`.
4. Reemplazar storage teorico por HTTP request real o simulacion explicita.

---

## 8. Decision Go / No-Go

### Go si se cumple esto

1. `SELECT * FROM matching_oportunidades(<vilma_uuid>)` devuelve oportunidades correctas.
2. Workflow `retar_decision` responde 200 con 3 preguntas.
3. La respuesta queda guardada en `decisiones`.
4. Hay MP3s o llamada real funcionando.
5. El presentador tiene una demo script de 3 minutos ensayada.

### No-Go si sigue asi

1. No hay workflow importable ni construido.
2. `demo/` sigue vacio.
3. `decisiones` sigue sin calzar con n8n.
4. No hay una fuente de verdad para datos.
5. Se intenta mostrar el modulo legal como si estuviera completo.

---

## 9. Diagnostico Final

COMPA tiene una buena idea y suficiente material para ganar atencion en un hackathon, pero no esta listo como sistema integrado. La prioridad no debe ser agregar mas features. La prioridad debe ser **cerrar una historia vertical completa**:

```text
Productor -> oportunidad detectada -> llamada o audio -> pregunta critica -> reasoning_trace -> guardado en Supabase -> evidencia en pantalla
```

Todo lo que no apoye esa ruta debe quedar como "siguiente fase" o "modulo experimental".

Mi recomendacion final es:

1. Mantener el pitch y la narrativa de transparencia.
2. Recortar demo a la ruta Vilma + oportunidades + retar decision.
3. Reparar schema/workflow antes de tocar el modulo legal.
4. Generar assets de demo inmediatamente.
5. Presentar honestamente que los datos de personas son sinteticos y los proveedores son reales.

Con esos ajustes, el proyecto puede pasar de prototipo inconsistente a demo convincente. Sin ellos, el riesgo principal es que falle en vivo por errores previsibles de integracion, no por limitaciones del concepto.
