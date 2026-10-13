# Iteración 05 · Proteger rutas y roles

[← 04 · Registro, login y JWT](04-registro-login-jwt.md) · [Índice](README.md) · [06 · Esqueleto en Angular →](06-angular-esqueleto.md) <!-- nav -->

**Clase:** martes 27 de octubre · **Entra en:** parcial 1 · **Duración:** 45 min · **Temas del plan:** seguridad, auditoría de código.

## Lo que vas a construir

La API completa: cada ruta exige un token válido, cada usuario ve solo lo que le corresponde y cada rol puede hacer solo lo que le toca. También el endpoint para que el admin gestione usuarios. Con esto se acaba el backend.

## Antes de programar

Completa esta tabla **antes** de escribir código. Para cada celda escribe el código de estado que debería responder la API: 200, 201, 204, 401 o 403.

| Petición | Sin token | `user` | `agent` | `admin` |
|---|---|---|---|---|
| `GET /api/tickets` | | | | |
| `POST /api/tickets` | | | | |
| `PATCH /api/tickets/1` | | | | |
| `DELETE /api/tickets/1` | | | | |
| `GET /api/users` | | | | |

Al final de la iteración la vas a verificar celda por celda.

## Conceptos

### Autenticación vs autorización

- **Autenticación:** ¿quién eres? Se resuelve con el token. Si falla: **401 Unauthorized**.
- **Autorización:** ¿puedes hacer esto? Se resuelve con el rol. Si falla: **403 Forbidden**.

El nombre "Unauthorized" del 401 confunde, pero en la práctica significa "no sé quién eres". El 403 significa "sé quién eres y no puedes".

![Diagrama de decisión: sin cabecera, token inválido o usuario inactivo da 401; rol no permitido da 403; si todo pasa se ejecuta el endpoint](img/05-autenticacion-autorizacion.svg)

### Cómo viaja el token

El cliente lo manda en una cabecera en cada petición:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiJ9...
```

*Bearer* significa "portador": quien porte el token tiene el acceso. Por eso un token robado es tan grave como una contraseña robada, y por eso vence.

### Dependencias que dependen de otras

En la iteración 03 usamos `Depends(get_db)` para conseguir una sesión. Ahora vamos a encadenar dependencias:

```
require_roles(admin)  ──necesita──▶  get_current_user  ──necesita──▶  bearer (lee la cabecera)
                                                       └─necesita──▶  get_db
```

FastAPI resuelve la cadena completa antes de ejecutar tu función. Si cualquier eslabón lanza un error, tu función ni siquiera se ejecuta. Así la regla de seguridad queda escrita **una sola vez** y no se te olvida en ninguna ruta.

### Una función que fabrica funciones

`require_roles(Role.admin)` no revisa nada por sí misma: **devuelve** otra función (`checker`) que es la que FastAPI ejecuta en cada petición. La función de adentro "recuerda" los roles con los que se creó. Esto se llama **clausura** (*closure*) y lo vas a ver otra vez en Angular, en la iteración 11.

## Paso a paso

### 1. Las dependencias de seguridad

Crea `backend/app/deps.py`:

```python
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from .database import get_db
from .models import Role, User
from .security import decode_token

bearer = HTTPBearer(auto_error=False)


def get_current_user(
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    unauthorized = HTTPException(
        status.HTTP_401_UNAUTHORIZED,
        "Token inválido o expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if creds is None:
        raise unauthorized
    user_id = decode_token(creds.credentials)
    user = db.get(User, user_id) if user_id else None
    if user is None or not user.is_active:
        raise unauthorized
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_roles(*roles: Role):
    def checker(user: CurrentUser) -> User:
        if user.role not in roles:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "No tienes permisos para esta acción")
        return user

    return checker
```

Lee `get_current_user` y responde: ¿en cuántos casos distintos responde 401? Deberías encontrar cuatro: no hay cabecera, el token es inválido o venció, el usuario ya no existe, o la cuenta está desactivada.

### 2. Protege los tickets

Reemplaza `backend/app/routers/tickets.py`:

```python
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import CurrentUser, require_roles
from ..models import Role, Ticket
from ..schemas import TicketIn, TicketOut, TicketUpdate

router = APIRouter(prefix="/tickets", tags=["tickets"])
DB = Annotated[Session, Depends(get_db)]


@router.get("", response_model=list[TicketOut])
def list_tickets(db: DB, user: CurrentUser):
    query = select(Ticket).order_by(Ticket.created_at.desc())
    if user.role == Role.user:  # los usuarios solo ven sus propios tickets
        query = query.where(Ticket.author_id == user.id)
    return db.scalars(query).all()


@router.post("", response_model=TicketOut, status_code=status.HTTP_201_CREATED)
def create_ticket(data: TicketIn, db: DB, user: CurrentUser):
    ticket = Ticket(**data.model_dump(), author_id=user.id)
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


@router.patch(
    "/{ticket_id}",
    response_model=TicketOut,
    dependencies=[Depends(require_roles(Role.agent, Role.admin))],
)
def update_ticket(ticket_id: int, data: TicketUpdate, db: DB):
    ticket = db.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Ticket no encontrado")
    ticket.status = data.status
    db.commit()
    db.refresh(ticket)
    return ticket


@router.delete(
    "/{ticket_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_roles(Role.admin))],
)
def delete_ticket(ticket_id: int, db: DB):
    ticket = db.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Ticket no encontrado")
    db.delete(ticket)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
```

Compara con la versión anterior:

- Desapareció `TEMP_AUTHOR_ID`. El autor sale del token (`user.id`), nunca del cuerpo de la petición.
- El filtro por rol está **en la consulta SQL**. No se traen todos los tickets para luego esconder algunos en el frontend: los ajenos ni siquiera salen de la base de datos.
- `dependencies=[...]` se usa cuando la función no necesita el usuario, solo que se haga la verificación.

### 3. Gestión de usuarios (solo admin)

Agrega a `backend/app/schemas.py`, debajo de `UserOut`:

```python
class UserUpdate(BaseModel):
    role: Role | None = None
    is_active: bool | None = None
```

Crea `backend/app/routers/users.py`:

```python
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import require_roles
from ..models import Role, User
from ..schemas import UserOut, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])
DB = Annotated[Session, Depends(get_db)]
Admin = Annotated[User, Depends(require_roles(Role.admin))]


@router.get("", response_model=list[UserOut])
def list_users(db: DB, _: Admin):
    return db.scalars(select(User).order_by(User.id)).all()


@router.patch("/{user_id}", response_model=UserOut)
def update_user(user_id: int, data: UserUpdate, db: DB, admin: Admin):
    if user_id == admin.id:
        # Evita que el último admin se quite el rol o se desactive a sí mismo
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "No puedes modificar tu propia cuenta")
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Usuario no encontrado")
    for field, value in data.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user
```

- `_: Admin`: el guion bajo es la convención para "necesito que esto se ejecute, pero no voy a usar el valor".
- `exclude_unset=True`: solo incluye los campos que el cliente **envió**. Si manda `{"role": "agent"}`, no se toca `is_active`. Eso es justo lo que significa `PATCH`: modificar una parte.
- `setattr(user, "role", "agent")` es lo mismo que escribir `user.role = "agent"`, pero con el nombre del campo en una variable.

En `backend/app/main.py`:

```python
from .routers import auth, tickets, users
```

```python
api.include_router(users.router)
```

## Comprueba

En `/docs`, el botón **Authorize** (arriba a la derecha) permite pegar un token para que se envíe en todas las peticiones.

Prepara los datos:

1. Registra a **Beto** (`beto@correo.com`). Ya tienes a **Ana** de la iteración anterior.
2. Haz login como admin (`admin@helpdesk.com` / `Admin12345`), copia el token y pégalo en **Authorize**.
3. `GET /api/users` para ver el id de Beto, y `PATCH /api/users/{id}` con `{"role": "agent"}`.

Ahora verifica tu tabla celda por celda: haz login con cada usuario, pon su token en **Authorize** y prueba. Para la columna "Sin token", usa **Logout** en el mismo botón.

Además:

- Con el token de Ana, crea un ticket. Con el de Beto (agent), lista los tickets: ¿ves el de Ana? Con Ana, ¿ves los tickets que creaste como admin en la iteración 03?
- Con el token de admin, intenta `PATCH /api/users/1` (tú mismo). Esperado: **400**.
- Con el admin, desactiva a Ana (`{"is_active": false}`) y luego intenta usar el token que **ya tenía** Ana. ¿Qué responde? ¿Por qué, si su token todavía no ha vencido?

## Para pensar

- ¿Por qué el filtro "solo mis tickets" se hace en la consulta SQL y no simplemente ocultando filas en el frontend?
- Un compañero propone quitar `get_current_user` del `GET /api/tickets` "porque igual el frontend solo muestra esa pantalla a usuarios logueados". ¿Qué le responderías?
- **Auditoría:** busca en tu código todas las rutas y verifica que cada una tenga alguna dependencia de seguridad, salvo `register`, `login` y `health`. Si encuentras una sin protección, ese es exactamente el tipo de error que un asistente de IA puede introducir sin avisar.

## Guarda tu avance

```bash
git add .
git commit -m "feat(api): autorización por roles y gestión de usuarios"
```

---

[← 04 · Registro, login y JWT](04-registro-login-jwt.md) · [Índice](README.md) · [06 · Esqueleto en Angular →](06-angular-esqueleto.md) <!-- nav -->
