from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import mailer
from ..database import get_db
from ..mailer import send_email
from ..deps import CurrentUser, require_roles
from ..models import Role, Ticket, TicketStatus
from ..schemas import TicketIn, TicketOut, TicketUpdate

router = APIRouter(prefix="/tickets", tags=["tickets"])
DB = Annotated[Session, Depends(get_db)]


@router.get("", response_model=list[TicketOut])
def list_tickets(db: DB, user: CurrentUser):
    query = select(Ticket).order_by(Ticket.created_at.desc())
    if user.role == Role.user:  # los usuarios solo ven sus propios tickets
        query = query.where(Ticket.author_id == user.id)
    return db.scalars(query).unique().all()


@router.post("", response_model=TicketOut, status_code=status.HTTP_201_CREATED)
def create_ticket(data: TicketIn, db: DB, user: CurrentUser, background: BackgroundTasks):
    ticket = Ticket(**data.model_dump(), author_id=user.id)
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    background.add_task(send_email, *mailer.ticket_created_author(ticket))
    for staff in mailer.staff_to_notify(db, exclude_id=user.id):
        background.add_task(send_email, *mailer.ticket_created_staff(ticket, staff))
    return ticket


@router.patch(
    "/{ticket_id}",
    response_model=TicketOut,
    dependencies=[Depends(require_roles(Role.agent, Role.admin))],
)
def update_ticket(ticket_id: int, data: TicketUpdate, db: DB, actor: CurrentUser, background: BackgroundTasks):
    ticket = db.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Ticket no encontrado")
    changed = ticket.status != data.status
    ticket.status = data.status
    db.commit()
    db.refresh(ticket)
    # Solo se avisa si el estado cambió de verdad y el autor no es quien lo cambió
    if changed and ticket.author_id != actor.id and ticket.status != TicketStatus.open:
        background.add_task(send_email, *mailer.ticket_status_changed(ticket))
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
