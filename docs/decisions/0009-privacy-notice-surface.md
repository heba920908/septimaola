# ADR-0009: Aviso de Privacidad como superficie informativa independiente

## Status

Proposed

## Context

El sitio React de Septima Ola esta enfocado principalmente en promocion,
contacto y presentacion publica del proyecto. Sin embargo, es necesario ofrecer
una superficie legal e informativa clara para comunicar la postura actual sobre
privacidad.

En este momento no se recaban, procesan ni almacenan datos personales desde el
sitio. Aun asi, publicar un aviso de privacidad aporta:

- Transparencia para personas usuarias y colaboradores
- Claridad de alcance legal en el estado actual del proyecto
- Base de evolucion para futuras funciones que pudieran involucrar datos

Al igual que se definio una superficie independiente para informacion
profesional en ADR-0006 (Press & Production Kit), el aviso de privacidad debe
mantenerse separado del flujo promocional principal para evitar mezclar
mensajes de marketing con contenido legal.

## Decision

Se define una nueva superficie independiente de Aviso de Privacidad en React,
con enrutamiento por hash y estructura modular paralela al Press Kit.

### Arquitectura de interfaz

- Ruta dedicada: `#/privacy-notice`
- Integracion en el enrutador ligero de `App.jsx` (mismo patron que
  `#/press-kit`)
- Componente dedicado: `react/src/components/privacy/PrivacyNotice.jsx`
- Navegacion de retorno al home mediante enlace `Volver`
- Descubrimiento desde footer y seccion de contacto

### Estructura de contenido (template regular)

El aviso sigue una estructura estandar y reconocible para privacidad:

1. Responsable
2. Datos personales recabados
3. Finalidades del tratamiento
4. Base legal y consentimiento
5. Transferencias de datos
6. Derechos ARCO y contacto
7. Conservacion
8. Medidas de seguridad
9. Cookies y tecnologias de rastreo
10. Cambios al aviso y vigencia

### Politica actual obligatoria

Mientras no exista captura de datos personales, cada seccion operativa debe
indicar explicitamente que **no aplica por el momento** o que **no se recaban
ni almacenan datos personales**, evitando ambiguedades.

Adicionalmente, debe declararse de forma expresa que la app de Facebook
registrada para el proyecto se usa unicamente para publicacion en canales
oficiales y no para recabar informacion de personas usuarias.

Si en el futuro se habilitan formularios, analitica identificable, newsletter,
o cualquier canal de captura, este aviso debera actualizarse en el mismo ciclo
de cambio del producto.

## Consequences

- Positivo: Mejora transparencia y confianza para usuarias/os y contrapartes.
- Positivo: Alinea contenido legal con una estructura estandar facil de
  mantener.
- Positivo: Deja preparado el sitio para escalar politicas de privacidad si
  cambia el modelo de datos.
- Neutral: Introduce una nueva superficie de contenido que requiere
  mantenimiento editorial.
- Riesgo: Puede existir desalineacion futura si se incorporan mecanismos de
  captura de datos sin actualizar el aviso en el mismo release.
