# 🎫 HelpDesk

Sistema de tickets de soporte para aprender un proyecto web completo: **Angular + FastAPI + PostgreSQL**, con autenticación **JWT**, **roles** y **correos** automáticos.

## Roles

| Rol | Puede |
|---|---|
| `user` | Registrarse, crear tickets y ver solo los suyos |
| `agent` | Ver todos los tickets y cambiar su estado |
| `admin` | Todo lo anterior, borrar tickets y gestionar usuarios (rol y activación) |

## Tecnologías

- **Frontend:** Angular 22 (componentes standalone, signals, lazy loading), pruebas con Vitest
- **Backend:** FastAPI, SQLAlchemy, PyJWT, bcrypt
- **Base de datos:** PostgreSQL 16 (Docker)
- **Correo:** [Mailpit](https://mailpit.axllent.org/) (servidor SMTP de desarrollo, Docker)

## Puesta en marcha

Requisitos: Docker y Node.js.

```bash
cp .env.example .env          # y cambia las claves
docker compose up -d --build  # PostgreSQL + API + Mailpit
cd frontend
npm install
npx ng serve
```

| Servicio | URL |
|---|---|
| Aplicación | http://localhost:4200 |
| API y documentación | http://localhost:8000/docs |
| Correos enviados (Mailpit) | http://localhost:8025 |

El administrador inicial es el definido en `ADMIN_EMAIL` / `ADMIN_PASSWORD` de tu `.env`.

## Correos que se envían

Bienvenida al registrarse · confirmación de ticket al autor · aviso de ticket nuevo a agentes y admins · cambio de estado al autor · cambio de rol y activación o desactivación de cuenta al usuario afectado.

## Pruebas

```bash
cd frontend
npx ng test --watch=false
```

## Estructura

```
backend/    API FastAPI (routers, modelos, seguridad JWT, correos)
frontend/   Aplicación Angular (core/ = servicios, guards, interceptor; pages/ = pantallas)
docs/       Guía de aprendizaje en PDF (Angular y fundamentos web) y el script que la genera
```

> La seguridad real vive en el backend: los guards y botones ocultos del frontend solo mejoran la experiencia.
