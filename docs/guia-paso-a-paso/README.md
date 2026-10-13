# Guía paso a paso: construye HelpDesk desde cero

Esta guía te lleva a construir, con tus propias manos, el sistema de tickets de este repositorio: un backend con **FastAPI + PostgreSQL** y un frontend con **Angular**.

No es una guía para copiar y pegar. Cada iteración te pide pensar antes de escribir código, te explica el concepto justo que necesitas y termina con algo que puedes ver funcionando. Si copias sin entender, el proyecto va a funcionar, pero tú no vas a saber por qué, y eso es lo que se evalúa.

## Cómo está organizada

Son 15 iteraciones cortas (30 a 45 minutos cada una) más una opcional. Cada iteración tiene la misma estructura:

| Sección | Para qué sirve |
|---|---|
| **Lo que vas a construir** | El resultado visible al terminar. |
| **Antes de programar** | Preguntas para responder en papel o en voz alta. Es la práctica de *specs before code*: primero se decide qué se va a hacer y después se escribe. |
| **Conceptos** | La teoría mínima, explicada con el código del proyecto. |
| **Paso a paso** | Archivos y comandos, en orden. |
| **Comprueba** | Cómo saber que funciona. Si no ves lo que se describe, no sigas. |
| **Para pensar** | Una o dos preguntas o retos cortos que obligan a usar lo aprendido. |
| **Guarda tu avance** | El commit de Git de esa iteración. |

## Ruta

| # | Iteración | Qué se aprende | Tema del plan de estudio |
|---|---|---|---|
| 00 | [Antes de empezar](00-antes-de-empezar.md) | Cliente-servidor, Docker, Git, reglas para usar IA | Arquitectura web, Git, asistentes de código |
| | **Bloque 1 · Backend** | | |
| 01 | [Tu primera API](01-primera-api.md) | HTTP, métodos, códigos de estado, JSON | Protocolo HTTP/HTTPS, cliente-servidor |
| 02 | [Base de datos y modelos](02-base-de-datos.md) | PostgreSQL, ORM, variables de entorno, hash de contraseñas | Arquitectura de sistemas web |
| 03 | [CRUD de tickets](03-crud-tickets.md) | Rutas, validación, esquemas de entrada y salida | Consumo de APIs REST (lado servidor) |
| 04 | [Registro, login y JWT](04-registro-login-jwt.md) | Autenticación, tokens firmados | Seguridad en sistemas web |
| 05 | [Proteger rutas y roles](05-proteger-rutas-roles.md) | Autorización, 401 vs 403, dependencias | Seguridad, auditoría de código |
| | **Bloque 2 · Frontend** | | |
| 06 | [Esqueleto en Angular](06-angular-esqueleto.md) | SPA, CSR/SSR, componentes, HTML semántico, Flexbox | HTML5, SEO, CSS, Flexbox, meta-frameworks |
| 07 | [TypeScript y señales](07-typescript-senales.md) | Tipos, estado con signals, control de flujo, ES6 funcional | TypeScript, programación funcional, estado |
| 08 | [Navegación con rutas](08-rutas.md) | Router, carga diferida | Rendimiento, SPA |
| 09 | [Login contra la API](09-http-login-cors.md) | Asincronismo, Observables, CORS | Event Loop, Promises, async/await, APIs REST |
| 10 | [Mantener la sesión](10-sesion-localstorage.md) | Servicios compartidos, LocalStorage, `computed` | Persistencia del lado del cliente |
| 11 | [Interceptor y guards](11-interceptor-guards.md) | Middleware en el cliente, protección de rutas | Arquitectura, seguridad |
| 12 | [Tickets conectados](12-tickets-conectados.md) | Servicio de datos, CRUD completo desde la interfaz | Consumo de APIs REST |
| 13 | [Panel de administración](13-panel-admin.md) | Roles en la interfaz, defensa en profundidad | Auditoría de seguridad |
| 14 | [Cierre: pruebas, despliegue e IA](14-cierre.md) | Pruebas, build, CI/CD, auditoría asistida por IA | CI/CD, despliegue, auditoría con IA, Git |
| + | [Extra: correos automáticos](extra-correos.md) | SMTP, tareas en segundo plano | Integración de servicios |

## Qué temas del plan quedan por fuera y por qué

El proyecto usa Angular, no React ni Next.js. Los conceptos son los mismos (componentes, estado, ciclo de vida, renderizado del lado del cliente o del servidor), así que en la iteración 06 hay una tabla que los compara. Tailwind CSS, IndexedDB y la integración con modelos de lenguaje aparecen como menciones o retos, no como iteraciones completas, porque no hay tiempo para profundizar en todo.

## Si te atascas

1. Lee el error completo. La mayoría de las veces dice exactamente qué archivo y qué línea fallan.
2. Revisa la sección **Comprueba** de la iteración anterior: casi siempre el problema viene de antes.
3. Compara tu archivo con el del proyecto de referencia (la carpeta `helpdesk-referencia` que clonas en la iteración 00). Ten en cuenta que en algunas iteraciones el código es una versión intermedia y en la referencia está la versión final.
4. Si le preguntas a una IA, pégale el error y el archivo, y pídele que te **explique** la causa. No aceptes un arreglo que no entiendas.

## Material complementario

La guía en PDF [`../guia-angular-helpdesk.pdf`](../guia-angular-helpdesk.pdf) recorre el proyecto ya terminado y explica cómo viaja un clic desde el navegador hasta la base de datos. Sirve como lectura antes o después de clase.
