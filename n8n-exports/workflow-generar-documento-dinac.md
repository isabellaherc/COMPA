# Compa — Asistente Legal DINAC: Workflow n8n "Generar Documento"

> **Webhook**: POST /generar-documento-dinac
> **Llamado por**: Tool `generar_documento` del agente ElevenLabs Compa
> **Nodos**: 9

---

## Workflow: Generar Documento DINAC (9 nodos)

### Trigger: Webhook
```
Node: Webhook
Path: /generar-documento-dinac
Method: POST
Response Mode: When Last Node Finishes
Timeout: 25s
```

**Request body (desde ElevenLabs):**
```json
{
  "tipo_documento": "declaracion_jurada_persona_natural",
  "productor_id": "a1000000-0000-0000-0000-000000000001",
  "datos_adicionales": {
    "fecha": "2026-07-04"
  }
}
```

---

### Node 1: Webhook (POST /generar-documento-dinac)
- Recibe: `tipo_documento`, `productor_id`, `datos_adicionales`

### Node 2: Postgres — Leer Productor
```sql
SELECT * FROM productores WHERE id = '{{ $json.body.productor_id }}'
```

### Node 3: Postgres — Leer Plantilla
```sql
SELECT * FROM plantillas_documentos WHERE tipo = '{{ $json.body.tipo_documento }}'
```

### Node 4: Code — Validar Campos
```javascript
const productor = $input.all()[0].json;
const plantilla = $input.all()[1].json;
const datosAdicionales = $input.all()[2].json.body.datos_adicionales || {};

// Extraer datos disponibles del productor
const datosProductor = {
  nombre: productor.nombre || '',
  dui: productor.dui || '',
  nit: productor.nit || '',
  direccion: productor.ubicacion || '',
  telefono: productor.telefono || '',
  rubro: productor.rubro || ''
};

// Merge con datos adicionales que dio en la llamada
const datosCompletos = { ...datosProductor, ...datosAdicionales };

// Validar campos requeridos
const camposRequeridos = plantilla.campos_requeridos;
const camposFaltantes = camposRequeridos.filter(campo => !datosCompletos[campo] || datosCompletos[campo] === '');

return {
  json: {
    productor_id: productor.id,
    plantilla_id: plantilla.id,
    tipo_documento: plantilla.tipo,
    datos_completos: datosCompletos,
    campos_faltantes: camposFaltantes,
    todo_completo: camposFaltantes.length === 0
  }
};
```

### Node 5: IF — ¿Faltan Campos?
```
Condition: {{ $json.todo_completo }} == false

TRUE → Node 5a: Respond with campos_faltantes
FALSE → Node 5b: Continue to Node 6
```

### Node 5a (TRUE): Respond to Webhook — Solicitar Datos
```json
{
  "estado": "incompleto",
  "campos_faltantes": ["nit", "fecha"],
  "mensaje": "Necesito algunos datos más para completar el documento. ¿Me podés dar tu NIT y la fecha de hoy?"
}
```

### Node 6: HTTP Request — Generar DOCX (opcional: servicio de mail-merge)
```
Method: POST
URL: {{ $env.DOCX_SERVICE_URL }}/merge  (o Code node si usamos docxtemplater en n8n)
Body: {
  "template_path": "{{ $json.plantilla_path }}",
  "data": {{ $json.datos_completos }}
}
```

**Alternativa simple (Code node) si no hay servicio externo:**
```javascript
// Para demo: en vez de generar DOCX real, devolver confirmación de merge
const datos = $input.first().json.datos_completos;
const tipo = $input.first().json.tipo_documento;

// En producción: usar docxtemplater.js o similar
return {
  json: {
    archivo_nombre: `${tipo}_${Date.now()}.docx`,
    datos_merge: datos,
    merge_status: 'simulado_demo'
  }
};
```

### Node 7: Supabase Storage — Subir Archivo
```
Operation: Upload
Bucket: documentos-dinac
File: {{ $json.archivo_nombre }}
Data: {{ $json.docx_content }}  (en producción: buffer del DOCX generado)
```

### Node 8: Postgres — INSERT en documentos_generados
```sql
INSERT INTO documentos_generados (productor_id, plantilla_id, datos_usados, archivo_url, estado)
VALUES (
  '{{ $json.productor_id }}',
  '{{ $json.plantilla_id }}',
  '{{ JSON.stringify($json.datos_merge) }}'::jsonb,
  '{{ $json.archivo_url }}',
  'borrador'
)
RETURNING id, archivo_url, estado
```

### Node 9: Respond to Webhook — Éxito
```json
{
  "estado": "borrador",
  "archivo_url": "https://xxx.supabase.co/storage/v1/object/public/documentos-dinac/declaracion_jurada_1712345678.docx",
  "mensaje": "Tu declaración jurada está lista como borrador. Revisala bien, imprimila, y firmala antes de presentarla. Esto no sustituye tu firma ni revisión personal."
}
```

---

## Error Handling (inline)

### Node 4b (ERROR): Productor no encontrado
```json
{
  "estado": "error",
  "error": "productor_no_encontrado",
  "mensaje": "No encontré tu perfil en el sistema. ¿Podés darme tus datos para registrarte primero?"
}
```

### Node 7b (ERROR): Fallo al subir archivo
```json
{
  "estado": "error",
  "error": "error_almacenamiento",
  "mensaje": "Tuve un problema guardando el archivo. Voy a intentar de nuevo. ¿Me confirmás que querés seguir?"
}
```
