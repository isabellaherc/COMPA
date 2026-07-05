# Fase 1 - Demo minima estable

## Fuente de verdad

Para la demo de Fase 1, `supabase-schema.sql` es la fuente unica de verdad. Los archivos JSON/CSV en `data/` quedan como material auxiliar o fallback, pero no deben usarse para decidir IDs, conteos ni matches en vivo.

## Ruta vertical cerrada

1. Ejecutar `supabase-schema.sql` en Supabase.
2. Obtener el productor principal:

```sql
SELECT id, nombre, rubro
FROM productores
WHERE nombre = 'Vilma Jeanneth Guardado de Ayala';
```

3. Obtener la oportunidad principal:

```sql
SELECT *
FROM matching_oportunidades(<vilma_uuid>, 5);
```

4. Confirmar persistencia de matches:

```sql
SELECT mo.*, p.nombre, o.titulo
FROM match_oportunidades mo
JOIN productores p ON p.id = mo.productor_id
JOIN oportunidades o ON o.id = mo.oportunidad_id
WHERE p.nombre = 'Vilma Jeanneth Guardado de Ayala'
ORDER BY mo.score DESC, o.monto DESC;
```

5. Enviar el payload de `demo/payload-retar-decision-vilma.json` al webhook `retar_decision`, reemplazando `productor_id` y `oportunidad_id` por UUIDs reales.

6. Verificar el guardado:

```sql
SELECT productor_id, oportunidad_id, conversation_id, preguntas_generadas, reasoning_trace, creado_en
FROM decisiones
WHERE conversation_id = 'demo-vilma-fase-1';
```

## Criterio de listo

La Fase 1 queda lista cuando:

- `matching_oportunidades(<vilma_uuid>, 5)` devuelve oportunidades de `Alimentos y Bebidas`.
- `match_oportunidades` contiene los matches de Vilma.
- `decisiones` acepta `productor_id` y `oportunidad_id` como UUID reales.
- El guion `demo/guion-demo-fase-1.md` se puede ejecutar aunque ElevenLabs o n8n no esten completos.