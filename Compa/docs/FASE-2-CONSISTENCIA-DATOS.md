# Fase 2 - Consistencia de datos

## Decisiones aplicadas

- `supabase-schema.sql` queda como fuente unica de verdad para productores, oportunidades y proveedores.
- Los archivos locales en `data/` se regeneran desde SQL con `scripts/export_sql_data.py`.
- Los IDs `prod-001`, `opp-001` y `prov-001` existen solo para fallback local; en Supabase y n8n se usan UUIDs reales.
- La lista cerrada de rubros queda exportada en `data/rubros-cerrados.json`.

## Cobertura corregida

Se agregaron oportunidades para los rubros que bloqueaban casos de demo:

- `Servicios Generales`: cubre a Ana Beatriz Cruz de Lemus.
- `Comercio y Distribucion`: cubre a Maria Susana Mejia Argueta.

Tambien se agrego un proveedor de `Servicios Generales` para evitar oportunidades sin proveedor asociado.

## Archivos regenerados

- `data/oportunidades.json`
- `data/fallback.json`
- `data/seed-oportunidades.csv`
- `data/productores.json`
- `data/proveedores.json`
- `data/seed-productores.csv`
- `data/rubros-cerrados.json`

## Comando de regeneracion

```powershell
C:\Users\isabe\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe Compa\scripts\export_sql_data.py
```

Salida esperada actual:

```text
Exported 15 productores, 43 oportunidades, 89 proveedores
Rubros sin oportunidades: []
Rubros sin proveedores: []
```

## Criterio de listo

La Fase 2 queda lista cuando:

- Los conteos de JSON/CSV coinciden con el SQL.
- `data/rubros-cerrados.json` reporta `sin_oportunidades: []`.
- `data/rubros-cerrados.json` reporta `sin_proveedores: []`.
- `Servicios Generales` y `Comercio y Distribucion` tienen al menos una oportunidad.