from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import mailer
from ..database import get_db
from ..mailer import send_email
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
def update_user(user_id: int, data: UserUpdate, db: DB, admin: Admin, background: BackgroundTasks):
    if user_id == admin.id:
        # Evita que el último admin se degrade o se desactive a sí mismo
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "No puedes modificar tu propia cuenta")
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Usuario no encontrado")
    old_role, old_active = user.role, user.is_active
    for field, value in data.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(user, field, value)
    db.commit()
    db.refresh(user)
    if user.role != old_role:
        background.add_task(send_email, *mailer.role_changed(user))
    if user.is_active != old_active:
        background.add_task(send_email, *mailer.account_status_changed(user))
    return user
