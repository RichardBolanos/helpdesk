# Guía paso a paso: construye HelpDesk desde cero

Esta guía te lleva a construir, con tus propias manos, el sistema de tickets de este repositorio: un backend con **FastAPI + PostgreSQL** y un frontend con **Angular**.

No es una guía para copiar y pegar. Cada iteración te pide pensar antes de escribir código, te explica el concepto justo que necesitas y termina con algo que puedes ver funcionando. Si copias sin entender, el proyecto va a funcionar, pero tú no vas a saber por qué, y eso es lo que se evalúa.

**Empieza aquí:** [00 · Antes de empezar →](00-antes-de-empezar.md) <!-- nav -->

## Cómo está organizada

Son 15 iteraciones cortas (30 a 45 minutos cada una), una tarea de JavaScript y una iteración opcional. Cada iteración tiene la misma estructura:

| Sección | Para qué sirve |
|---|---|
| **Lo que vas a construir** | El resultado visible al terminar. |
| **Antes de programar** | Preguntas para responder en papel o en voz alta. Es la práctica de *specs before code*: primero se decide qué se va a hacer y después se escribe. |
| **Conceptos** | La teoría mínima, explicada con el código del proyecto. |
| **Paso a paso** | Archivos y comandos, en orden. |
| **Comprueba** | Cómo saber que funciona. Si no ves lo que se describe, no sigas. |
| **Para pensar** | Preguntas y retos cortos que obligan a usar lo aprendido. En clase no siempre hay tiempo para hacerlos, pero de aquí salen las preguntas de los parciales. |
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
| tarea | [JavaScript mínimo para Angular](06b-javascript-minimo.md) | Funciones flecha, `map`/`filter`, spread, `?.`, `??`, clases, módulos | Programación funcional en JavaScript (ES6+), modularidad |
| 07 | [TypeScript y señales](07-typescript-senales.md) | Tipos, estado con signals, control de flujo, ES6 funcional | TypeScript, programación funcional, estado |
| 08 | [Navegación con rutas](08-rutas.md) | Router, carga diferida | Rendimiento, SPA |
| 09 | [Login contra la API](09-http-login-cors.md) | Asincronismo, Observables, CORS | Event Loop, Promises, async/await, APIs REST |
| 10 | [Mantener la sesión](10-sesion-localstorage.md) | Servicios compartidos, LocalStorage, `computed` | Persistencia del lado del cliente |
| 11 | [Interceptor y guards](11-interceptor-guards.md) | Middleware en el cliente, protección de rutas | Arquitectura, seguridad |
| 12 | [Tickets conectados](12-tickets-conectados.md) | Servicio de datos, CRUD completo desde la interfaz | Consumo de APIs REST |
| 13 | [Panel de administración](13-panel-admin.md) | Roles en la interfaz, defensa en profundidad | Auditoría de seguridad |
| 14 | [Cierre: pruebas, despliegue e IA](14-cierre.md) | Pruebas, build, CI/CD, auditoría asistida por IA | CI/CD, despliegue, auditoría con IA, Git |
| + | [Extra: correos automáticos](extra-correos.md) | SMTP, tareas en segundo plano | Integración de servicios |

## Cronograma 2026-2

Clases los martes, 3 horas. Cada sesión cubre el *Paso a paso* y el *Comprueba* de sus iteraciones. Si no terminas en clase, termínalo antes de la siguiente: cada iteración depende de la anterior.

| Fecha | Iteraciones | Al terminar tienes |
|---|---|---|
| Oct 13 | 00–01 (incluye instalar las herramientas) | Tu primera API corriendo en Docker |
| Oct 20 | 02–04 | Base de datos, CRUD de tickets, registro y login |
| Oct 27 | 05–06 | Backend completo con roles y el esqueleto en Angular |
| **Nov 3** | **Parcial 1** (iteraciones 00–06) | |
| Antes del Nov 10 | Tarea: [JavaScript mínimo](06b-javascript-minimo.md) | El JavaScript moderno que usa Angular |
| Nov 10 | 07–09 | Pantallas con rutas y login real contra la API |
| Nov 17 | 10–12 | Sesión, guards y tickets conectados |
| Nov 24 | 13–14 y ponerse al día | Aplicación completa, pruebas y CI |
| **Dic 1** | **Parcial 2** (todo el proyecto) | |

La sesión del 24 de noviembre es más corta a propósito: deja margen para quien vaya atrasado antes del parcial final. La iteración extra de correos no está en el cronograma; es opcional.

## Evaluación: el parcial es sobre tu proyecto

Los parciales se hacen sobre **tu propio repositorio**, no sobre el de referencia. Para presentarlo necesitas:

1. Tener en tu repositorio un commit por cada iteración evaluada, con las fechas en que trabajaste.
2. Tener el proyecto corriendo en tu computador al empezar el parcial.

En el parcial puede pasar cualquiera de estas cosas:

- Explicar un archivo o un flujo de tu código (por ejemplo, qué pasa desde que oprimes *Entrar* hasta que ves los tickets).
- Predecir qué código de estado responde la API en una situación dada, y luego comprobarlo.
- Responder preguntas de las secciones *Antes de programar* y *Para pensar*.
- Hacer un cambio pequeño en vivo y sin IA: un campo nuevo, un endpoint, un filtro, una regla de permisos.

Si el código está en tu repositorio pero no lo puedes explicar, para la nota es como si no estuviera.

## Qué se asume que ya sabes

HTML, CSS y Bootstrap básicos, y JavaScript básico (variables, condicionales, ciclos y funciones). Python, HTTP, bases de datos y TypeScript se explican desde cero.

El JavaScript que usa Angular va bastante más allá de lo básico. Por eso, entre el parcial 1 y la clase del 10 de noviembre, hay una tarea: [JavaScript mínimo para Angular](06b-javascript-minimo.md). Sin ella, el bloque de Angular se vuelve copiar sin entender.

## Qué temas del plan quedan por fuera y por qué

El proyecto usa Angular, no React ni Next.js. Los conceptos son los mismos (componentes, estado, ciclo de vida, renderizado del lado del cliente o del servidor), así que en la iteración 06 hay una tabla que los compara. Tailwind CSS, IndexedDB y la integración con modelos de lenguaje aparecen como menciones o retos, no como iteraciones completas, porque no hay tiempo para profundizar en todo.

## Si te atascas

1. Lee el error completo. La mayoría de las veces dice exactamente qué archivo y qué línea fallan.
2. Revisa la sección **Comprueba** de la iteración anterior: casi siempre el problema viene de antes.
3. Compara tu archivo con el del proyecto de referencia (la carpeta `helpdesk-referencia` que clonas en la iteración 00). Ten en cuenta que en algunas iteraciones el código es una versión intermedia y en la referencia está la versión final.
4. Si le preguntas a una IA, pégale el error y el archivo, y pídele que te **explique** la causa. No aceptes un arreglo que no entiendas.

## Material complementario

La guía en PDF [`../guia-angular-helpdesk.pdf`](../guia-angular-helpdesk.pdf) recorre el proyecto ya terminado y explica cómo viaja un clic desde el navegador hasta la base de datos. Sirve como lectura antes o después de clase.

---

**Empieza aquí:** [00 · Antes de empezar →](00-antes-de-empezar.md) <!-- nav -->
