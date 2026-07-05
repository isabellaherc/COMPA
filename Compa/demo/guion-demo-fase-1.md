# COMPA - Guion de Demo Fase 1

Objetivo: mostrar una sola ruta vertical estable con Vilma.

## Ruta

1. Productora principal: Vilma Jeanneth Guardado de Ayala.
2. Fuente de verdad: Supabase, usando `supabase-schema.sql`.
3. Match: `SELECT * FROM matching_oportunidades(<vilma_uuid>, 5);`.
4. Llamada simulada: usar este guion en vez de prometer audio real si ElevenLabs no esta listo.
5. Retar decision: enviar el payload de `demo/payload-retar-decision-vilma.json` al webhook n8n.
6. Evidencia: mostrar la fila guardada en `decisiones` con `conversation_id = 'demo-vilma-fase-1'`.

## Guion de llamada

Compa: Dona Vilma, como esta? Habla Compa. Vi una oportunidad para servicio de alimentacion escolar en La Libertad por 48,750 dolares. Tiene cierre el 18 de julio de 2026. Le cuento rapido?

Vilma: Si, me interesa, pero me preocupa si puedo cumplir con el volumen y esperar el pago.

Compa: Tiene sentido. Antes de decidir, revisemos tres puntos: costo unitario, flujo de caja para aguantar el pago del Estado, y plan B si gana pero la demanda supera su capacidad.

## Preguntas esperadas

1. Ya calculo cuanto le cuesta producir cada almuerzo con los precios actuales?
2. Tiene flujo de caja para aguantar 60 a 90 dias antes del pago?
3. Que plan B tiene si gana y no puede cumplir con la cantidad completa?

## Consulta para obtener IDs reales

```sql
SELECT
  p.id AS productor_id,
  m.oportunidad_id,
  p.nombre AS nombre_productor,
  m.titulo AS oportunidad_titulo,
  m.institucion AS oportunidad_institucion,
  m.monto AS oportunidad_monto,
  m.fecha_cierre AS oportunidad_cierre
FROM productores p
JOIN LATERAL matching_oportunidades(p.id, 1) m ON true
WHERE p.nombre = 'Vilma Jeanneth Guardado de Ayala';
```

Copiar `productor_id` y `oportunidad_id` al payload antes de llamar n8n. No usar el nombre ni `conversation_id` como llave foranea.