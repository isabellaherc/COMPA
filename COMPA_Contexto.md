# Compa — Contexto del proyecto

## ¿Qué es?

Compa es un "socio" digital con voz, pensado para MYPE y cooperativas salvadoreñas que venden al Estado. Detecta oportunidades de negocio, las explica por voz, ayuda a decidir si conviene participar, y organiza cotizaciones entre proveedores. No es un chatbot ni un sistema de alertas: conversa con el productor como lo haría un asesor humano.

## Problema

Las MYPE y cooperativas salvadoreñas:
- No se enteran a tiempo de oportunidades publicadas en **COMPRASAL** (el sistema de compras públicas de El Salvador).
- No siempre saben si una oportunidad les conviene o si tienen capacidad real para cumplirla.
- Pierden días haciendo llamadas para conseguir cotizaciones de insumos.

## Solución

Un asistente con voz (ElevenLabs) orquestado por flujos automatizados (n8n) que:
1. **Detecta** oportunidades relevantes según el rubro y ubicación del productor.
2. **Llama** o envía una nota de voz explicando la oportunidad en lenguaje simple.
3. **Escucha** la respuesta del productor (nota de voz) y genera "preguntas duras" — las que un asesor humano haría antes de decidir.
4. (Opcional / a futuro) **Organiza cotizaciones** entre proveedores para los insumos que el productor necesita.

## Usuarios

Productor, MYPE o cooperativa que ya provee o quiere proveer al Estado salvadoreño.

## Los tres módulos del producto

| Módulo | Qué hace |
|---|---|
| **Oportunidades** | Detecta y explica oportunidades de COMPRASAL que hacen match con el perfil del productor. |
| **Cofundador** | Recibe la respuesta del productor, genera preguntas críticas, y responde con voz para ayudarlo a decidir. |
| **Subasta Inversa** | Organiza cotizaciones entre proveedores privados de insumos (módulo de menor prioridad, a futuro). |

## Bolsa de empresas ampliada: "quién más vende al Estado"

Compa no debe limitarse a mostrar oportunidades sueltas: también debe mostrarle al productor **el resto de la red de proveedores que ya venden al Estado en su mismo rubro** — sus competidores reales, no ficticios. Esto responde directamente a la pregunta que un productor se hace al ver una oportunidad: *"¿quién más está compitiendo por esto?"*

**Fuente de datos:** COMPRASAL/RUPES publica un **Listado de Proveedores del Estado** de acceso público — el Registro Único de Proveedores del Estado completo, con el rubro/giro de cada proveedor ya inscrito. COMPRASAL también publica una **Consulta Pública del Registro de Sanciones**, que indica si un proveedor ha sido sancionado.

Esto significa que la expansión de la "bolsa de empresas" no requiere scraping de bases de datos privadas ni de directorios comerciales de pago (esos no son información pública real y no deben usarse). Basta con cachear estos dos listados públicos de COMPRASAL/RUPES, igual que ya se hace con las oportunidades.

**Qué habilita esto:**
- Ver, para cada oportunidad o rubro, qué otros proveedores del RUPES ya operan en ese mismo giro (competidores reales).
- Marcar si algún proveedor de la lista tiene sanciones registradas (señal de confianza).
- Dar insumo real al módulo de Subasta Inversa: en vez de un contacto ficticio, se puede mostrar un proveedor real registrado en RUPES como candidato a cotizar.

**Qué no cambia:** el marco legal sigue igual — esta información ya es pública por definición legal del RUPES, Compa solo la muestra, no la modifica ni la usa para representar a nadie.

## Núcleo obligatorio del proyecto

Independientemente de cómo se construya después, dos cosas son innegociables en Compa:

- **La orquestación de todos los flujos se hace mediante n8n.**
- **La voz del asistente se genera con ElevenLabs**, y es siempre la misma voz (el mismo "personaje"), sin importar qué módulo esté hablando.

Además, Compa se apoya en un modelo de lenguaje para razonar, clasificar oportunidades y generar las preguntas duras; y en datos de COMPRASAL que se usan siempre de forma cacheada, nunca extraídos en vivo durante una interacción con el usuario.

## Marco legal — lo esencial

- Compa se apoya en la **Ley de Compras Públicas**, **COMPRASAL** y el **RUPES**, pero **no participa en el procedimiento administrativo**: no oferta, no firma, no adjudica, no representa jurídicamente al proveedor. Solo asiste.
- Toda oportunidad mostrada proviene de una fuente pública y nunca se modifica.
- Toda recomendación de la IA es una sugerencia, nunca una decisión vinculante, y debe poder rastrearse a un documento oficial.
- Las llamadas de ElevenLabs requieren consentimiento previo del usuario.
- En producción aplicaría la Ley de Protección de Datos Personales (Decreto 144/2024); en cualquier demo o prototipo se usan datos ficticios o el dataset público cacheado.

## Reglas de negocio esenciales

- **RN-001** — Un usuario necesita un perfil de negocio (rubro, ubicación, capacidad) antes de recibir recomendaciones.
- **RN-002 / RN-004** — Toda oportunidad viene de COMPRASAL y Compa nunca la modifica.
- **RN-003** — Solo se muestran oportunidades que hacen match con el rubro del negocio.
- **RN-005** — Toda explicación generada por IA conserva un enlace o referencia a la fuente oficial.
- **RN-006** — Las recomendaciones son sugerencias, nunca decisiones obligatorias.
- **RN-009** — Toda llamada de ElevenLabs requiere consentimiento previo.
- **RN-010** — Las negociaciones simuladas con proveedores privados no sustituyen la Subasta Electrónica Inversa regulada por la LCP.
- RN-007 y RN-008 (confidencialidad de cotizaciones e historial) existen pero son de menor prioridad de implementación.

## Diferenciador clave

Compa no es un sistema de notificaciones. La diferencia está en la **conversación**: llama, explica, y hace las preguntas críticas que ayudan a decidir — algo que una alerta o un correo automático no puede hacer.

## Qué está dentro y fuera de alcance (versión prototipo/hackathon)

**Dentro:**
- Flujo completo: detección de oportunidad → explicación por voz → respuesta del productor → preguntas duras → resumen.

**Fuera:**
- Subasta Inversa real con proveedores.
- Firma electrónica.
- Integración con la API oficial de COMPRASAL (se usa dataset cacheado).
- Cualquier trámite legal o constitutivo.
- Dashboard de administración.
