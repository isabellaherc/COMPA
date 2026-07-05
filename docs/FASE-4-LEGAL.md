# Fase 4 - Legal como módulo secundario

## Separación corregida

La confusión venía de mezclar dos usos distintos de la carpeta legal:

- `DocumentacionLegal/Documentación-usuario/`: plantillas y formularios para documentos que COMPA puede preparar para el usuario.
- `DocumentacionLegal/Leyes y reglamentos/`, `DocumentacionLegal/Lineamientos/`, `DocumentacionLegal/Políticas/` e `Información DINAC.txt`: repositorio de información legal para Knowledge Base/RAG.

## Entregables

- `data/legal-template-manifest.json`: inventario de plantillas generables.
- `data/legal-kb-repository-manifest.json`: inventario del repositorio legal.
- `data/legal-kb-curated-elevenlabs.json`: subconjunto recomendado para subir al Knowledge Base.
- `n8n-exports/workflow-generar-documento-dinac.json`: workflow importable para generar un borrador simulado y auditarlo en Supabase.
- `n8n-exports/elevenlabs-tool-generar-documento.json`: definición del tool para copiar al dashboard de ElevenLabs.
- `demo/payload-generar-documento-vilma.mock.json`: payload de prueba.
- `scripts/test_phase4_contract.py`: validación estática del contrato.

## Tamaños locales

- Plantillas de usuario: 21 archivos, 4240524 bytes.
- Repositorio legal completo: 38 archivos, 160615558 bytes.
- Subconjunto RAG recomendado: 8 archivos, 25471512 bytes.

## Regla de demo

El módulo legal no es la ruta principal de demo. Si se muestra, debe declararse como módulo secundario en modo borrador:

1. Pregunta legal: responder con RAG del repositorio legal, citando fuente.
2. Documento: usar `generar_documento` sobre plantillas de `Documentación-usuario`.
3. Resultado: siempre `estado = borrador`; nunca decir firmado, presentado o aprobado.

## Variables requeridas

- `COMPA_WEBHOOK_SECRET` opcional, default `whsec_compa_buildathon_2026`.
- Credential n8n `Supabase Postgres` para los nodos Postgres.

## Prueba local

```powershell
C:\Users\isabe\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe Compa\scripts\test_phase4_contract.py
```

Salida esperada:

```text
phase4 contract ok
```
