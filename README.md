# 🎫 HelpDesk

Sistema de tickets de soporte para aprender un proyecto web completo: **Angular + FastAPI + PostgreSQL**, con autenticación **JWT**, **roles** y **correos** automáticos.

> Proyecto **educativo**. Por eso el archivo `.env` (con claves de desarrollo) está incluido en el repositorio: así puedes arrancarlo sin configurar nada. **Nunca hagas esto en un proyecto real.**

## Qué aprenderás con él

HTTP y sus métodos (GET, POST, PATCH, DELETE), el DOM, CSS, componentes de Angular, servicios, interceptores y guards, JWT, roles, CORS, Docker y envío de correos.

## Para estudiantes de Programación Web 1 (2026-2)

Este repositorio es el **proyecto de referencia**: la versión terminada. Tú no lo vas a copiar, lo vas a **construir desde cero** en tu propio repositorio siguiendo la guía:

**[Guía paso a paso →](docs/guia-paso-a-paso/README.md)**

- Son 15 iteraciones cortas, una o varias por clase. El cronograma con las fechas está en la guía.
- **El proyecto es lo que se evalúa en los dos parciales** (3 de noviembre y 1 de diciembre). Los parciales se hacen sobre tu repositorio: debes tenerlo al día, con un commit por iteración, y corriendo en tu computador. Los detalles están en la sección *Evaluación* de la guía.
- Usa este repositorio para comparar cuando te atasques. Las instrucciones de abajo sirven para correrlo y ver cómo debe quedar el tuyo.

Como lectura complementaria está la guía en PDF, que recorre el proyecto terminado y explica cómo viaja un clic desde el navegador hasta la base de datos: [`docs/guia-angular-helpdesk.pdf`](docs/guia-angular-helpdesk.pdf).

## Roles

| Rol | Puede |
|---|---|
| `user` | Registrarse, crear tickets y ver solo los suyos |
| `agent` | Ver todos los tickets y cambiar su estado |
| `admin` | Todo lo anterior, borrar tickets y gestionar usuarios (rol y activación) |

## Tecnologías

- **Frontend:** Angular 22 (componentes standalone, signals, carga diferida), pruebas con Vitest
- **Backend:** FastAPI, SQLAlchemy, PyJWT, bcrypt
- **Base de datos:** PostgreSQL 16 (Docker)
- **Correo:** [Mailpit](https://mailpit.axllent.org/), un servidor SMTP de desarrollo (Docker). Los correos **no salen a internet**: los ves en una web local.

---

## Cómo correr el proyecto desde cero

### Paso 0 · Instala los requisitos

Necesitas tres programas. **No hace falta instalar Python**: el backend corre dentro de Docker.

| Programa | Para qué | Descarga |
|---|---|---|
| **Git** | Descargar el proyecto | https://git-scm.com/downloads |
| **Docker Desktop** | Base de datos, API y correos | https://www.docker.com/products/docker-desktop |
| **Node.js** 22.22.3+, 24.15+ o 26+ | Frontend de Angular | https://nodejs.org (elige la versión LTS más reciente) |

Comprueba que quedaron instalados (cada comando debe mostrar una versión, no un error):

```bash
git --version
docker --version
node --version
```

Luego **abre Docker Desktop y espera** a que diga *"Engine running"*. Si Docker está apagado, el paso 3 falla.

### Paso 1 · Descarga el proyecto

```bash
git clone https://github.com/RichardBolanos/helpdesk.git helpdesk-referencia
cd helpdesk-referencia
```

Se clona con el nombre `helpdesk-referencia` para que no choque con la carpeta `helpdesk` donde construyes tu propio proyecto con la guía. En el resto de este archivo, "la carpeta del proyecto" es `helpdesk-referencia/`.


### Paso 2 · Revisa la configuración (opcional)

El archivo [`.env`](.env) ya viene listo con valores de desarrollo; **no necesitas tocar nada** para empezar. Contiene, entre otras cosas:

| Variable | Qué es | Valor por defecto |
|---|---|---|
| `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` | Credenciales de la base de datos | `helpdesk` / `helpdesk_dev_pw` / `helpdesk` |
| `SECRET_KEY` | Clave con la que se firman los JWT | clave de desarrollo |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Duración de la sesión | `60` |
| `ADMIN_EMAIL` / `ADMIN_PASSWORD` | Administrador inicial | `admin@helpdesk.com` / `Admin12345` |
| `CORS_ORIGINS` | Dirección del frontend autorizada | `http://localhost:4200` |

### Paso 3 · Levanta el backend (base de datos + API + correos)

Desde la carpeta del proyecto (`helpdesk-referencia/`):

```bash
docker compose up -d --build
```

La primera vez descarga imágenes y puede tardar unos minutos. Al terminar, comprueba que los tres servicios estén en marcha:

```bash
docker compose ps
```

Debes ver `db` (healthy), `api` y `mailpit` con estado *Up*. Para confirmar que la API responde, abre http://localhost:8000/docs: verás la documentación interactiva de todos los endpoints.

El administrador inicial se crea automáticamente al arrancar.

### Paso 4 · Levanta el frontend

En **otra terminal**, desde la carpeta del proyecto:

```bash
cd frontend
npm install
npx ng serve
```

`npm install` descarga las dependencias (solo la primera vez). Cuando `ng serve` termine de compilar, abre http://localhost:4200.

### Paso 5 · Pruébalo

1. Entra con el administrador: **`admin@helpdesk.com`** / **`Admin12345`**.
2. Cierra sesión (botón *Salir*), pulsa **Regístrate** y crea un usuario normal (contraseña de 8 caracteres o más).
3. Con ese usuario, crea un ticket. Verás la lista actualizada al instante.
4. Vuelve a entrar como admin: en **Tickets** cambia el estado a *in_progress* o *closed*, y en **Usuarios** cambia el rol del usuario a *agent*.
5. Abre http://localhost:8025 (**Mailpit**): ahí están los correos que se enviaron en cada paso (bienvenida, ticket recibido, cambio de estado, cambio de rol...).

### Direcciones del proyecto

| Servicio | URL |
|---|---|
| Aplicación (Angular) | http://localhost:4200 |
| API y documentación (FastAPI) | http://localhost:8000/docs |
| Correos enviados (Mailpit) | http://localhost:8025 |
| PostgreSQL (para DBeaver, etc.) | `localhost:5433` · usuario y clave del `.env` |

> PostgreSQL se publica en el puerto **5433** (y no en el 5432 habitual) para no chocar con un Postgres que ya tengas instalado.

---

## Comandos del día a día

| Qué quieres hacer | Comando |
|---|---|
| Apagar todo (conserva los datos) | `docker compose down` |
| Volver a encender | `docker compose up -d` |
| Ver los registros de la API | `docker compose logs -f api` |
| **Borrar todos los datos** y empezar limpio | `docker compose down -v` |
| Ejecutar las pruebas del frontend | `cd frontend && npx ng test --watch=false` |
| Compilar el frontend para producción | `cd frontend && npx ng build` |

El código de la API se recarga solo al guardar (carpeta `backend/app` montada en el contenedor). El del frontend también, gracias a `ng serve`.

## Si algo falla

| Síntoma | Causa y solución |
|---|---|
| `failed to connect to the docker API` / `docker daemon is not running` | Docker Desktop está apagado. Ábrelo y espera a *Engine running*. |
| `port is already allocated` o `address already in use` | Otro programa usa 8000, 8025 o 4200. Ciérralo, o cambia el puerto izquierdo en `docker-compose.yml` (por ejemplo `"8001:8000"`). Si cambias el del frontend, añade ese origen a `CORS_ORIGINS` en `.env`. |
| El login dice *"No se pudo conectar con el servidor"* | La API no está corriendo. Revisa `docker compose ps` y `docker compose logs api`. |
| En la consola del navegador aparece un error de **CORS** | El frontend está en una dirección distinta a `http://localhost:4200`. Usa esa, o agrégala a `CORS_ORIGINS` y ejecuta `docker compose up -d --force-recreate api`. |
| `npm install` falla o `ng` no se reconoce | Versión de Node demasiado antigua: comprueba `node --version` (necesitas 22.22.3 o superior, 24.15+ o 26+). Si usas `nvm`, ejecuta `nvm install --lts`. |
| `npm install` muestra avisos `npm warn install-scripts` | Es normal con npm 11: avisa de scripts opcionales de aceleración que no se ejecutan. La instalación funciona igual; ignóralos. |
| Registro con error *"Datos inválidos"* | El email debe tener un dominio real (no se aceptan `.local`) y la contraseña entre 8 y 72 caracteres. |
| Cambié el `.env` y no se nota | Los contenedores leen el `.env` al crearse: ejecuta `docker compose up -d --force-recreate`. |

## API (resumen)

Base: `http://localhost:8000/api`. Todas las rutas, salvo registro y login, requieren la cabecera `Authorization: Bearer <token>`.

| Método y ruta | Quién puede | Qué hace |
|---|---|---|
| `POST /auth/register` | Cualquiera | Crea una cuenta con rol `user` |
| `POST /auth/login` | Cualquiera | Devuelve el JWT y el usuario |
| `GET /tickets` | Autenticados | `user`: solo los suyos · `agent`/`admin`: todos |
| `POST /tickets` | Autenticados | Crea un ticket |
| `PATCH /tickets/{id}` | `agent`, `admin` | Cambia el estado |
| `DELETE /tickets/{id}` | `admin` | Borra un ticket |
| `GET /users` | `admin` | Lista usuarios |
| `PATCH /users/{id}` | `admin` | Cambia rol o activación |

## Correos que se envían

Bienvenida al registrarse · confirmación de ticket al autor · aviso de ticket nuevo a agentes y admins · cambio de estado al autor · cambio de rol y activación o desactivación de cuenta al usuario afectado.

## Estructura

```
backend/    API FastAPI (routers, modelos, seguridad JWT, correos)
frontend/   Aplicación Angular
  src/app/core/    servicios, interceptor y guards (cada uno con su .spec.ts)
  src/app/pages/   una carpeta por pantalla: .ts + .html + .css + .spec.ts
docs/
  guia-paso-a-paso/          guía para construir el proyecto desde cero, cronograma y evaluación
  guia-angular-helpdesk.pdf  recorrido del proyecto terminado (y build_guia.py, que lo genera)
```

> La seguridad real vive en el backend: los guards y botones ocultos del frontend solo mejoran la experiencia.
