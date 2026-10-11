import logging
import smtplib
from email.message import EmailMessage
from html import escape

from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import settings
from .models import Role, Ticket, TicketStatus, User

log = logging.getLogger("helpdesk.mail")

STATUS_LABEL = {
    TicketStatus.open: "abierto",
    TicketStatus.in_progress: "en atención",
    TicketStatus.closed: "cerrado",
}
ROLE_LABEL = {Role.user: "usuario", Role.agent: "agente", Role.admin: "administrador"}


def _one_line(text: str) -> str:
    # Evita inyección de cabeceras: los saltos de línea no pueden llegar al asunto
    return " ".join(text.split())


def send_email(to: str, subject: str, lines: list[str]) -> None:
    """Envía un correo (texto + HTML). Pensado para BackgroundTasks: nunca lanza excepciones."""
    msg = EmailMessage()
    msg["From"] = settings.mail_from
    msg["To"] = to
    msg["Subject"] = _one_line(subject)
    msg.set_content("\n\n".join(lines) + f"\n\nHelpDesk: {settings.frontend_url}")
    paragraphs = "".join(f"<p>{escape(line)}</p>" for line in lines)  # escape: el contenido viene de usuarios
    msg.add_alternative(
        f"<div style='font-family:sans-serif'><h2>🎫 HelpDesk</h2>{paragraphs}"
        f"<p><a href='{escape(settings.frontend_url)}'>Abrir HelpDesk</a></p></div>",
        subtype="html",
    )
    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as smtp:
            smtp.send_message(msg)
    except Exception:
        # Un fallo de correo no debe romper la operación del usuario
        log.exception("No se pudo enviar el correo a %s (%s)", to, subject)


# --- Plantillas por evento. Devuelven (destinatario, asunto, líneas). ---

def welcome(user: User):
    return user.email, "Bienvenido a HelpDesk", [
        f"Hola {user.name}, tu cuenta se creó correctamente.",
        "Ya puedes iniciar sesión y abrir tickets de soporte.",
    ]


def ticket_created_author(ticket: Ticket):
    return ticket.author.email, f"Ticket #{ticket.id} recibido: {ticket.title}", [
        f"Hola {ticket.author.name}, hemos recibido tu solicitud.",
        f"Ticket #{ticket.id} — {ticket.title} (prioridad {ticket.priority.value}).",
        "Te avisaremos cuando cambie su estado.",
    ]


def ticket_created_staff(ticket: Ticket, staff: User):
    return staff.email, f"[{ticket.priority.value}] Nuevo ticket #{ticket.id}: {ticket.title}", [
        f"Hola {staff.name}, {ticket.author.name} abrió un nuevo ticket.",
        f"#{ticket.id} — {ticket.title} (prioridad {ticket.priority.value}).",
        ticket.description,
    ]


def ticket_status_changed(ticket: Ticket):
    label = STATUS_LABEL[ticket.status]
    detail = (
        "Lo damos por resuelto. Si el problema continúa, abre un nuevo ticket."
        if ticket.status == TicketStatus.closed
        else "Nuestro equipo ya está trabajando en él."
    )
    return ticket.author.email, f"Ticket #{ticket.id} ahora está {label}", [
        f"Hola {ticket.author.name}, tu ticket #{ticket.id} «{ticket.title}» ahora está {label}.",
        detail,
    ]


def role_changed(user: User):
    return user.email, "Tu rol en HelpDesk ha cambiado", [
        f"Hola {user.name}, tu rol ahora es: {ROLE_LABEL[user.role]}.",
        "Es posible que debas volver a abrir la página para ver tus nuevos permisos.",
    ]


def account_status_changed(user: User):
    if user.is_active:
        return user.email, "Tu cuenta de HelpDesk fue reactivada", [
            f"Hola {user.name}, tu cuenta fue reactivada. Ya puedes iniciar sesión."
        ]
    return user.email, "Tu cuenta de HelpDesk fue desactivada", [
        f"Hola {user.name}, tu cuenta fue desactivada y ya no podrás iniciar sesión.",
        "Si crees que es un error, contacta con un administrador.",
    ]


def staff_to_notify(db: Session, exclude_id: int) -> list[User]:
    """Agentes y admins activos, salvo quien creó el ticket."""
    query = select(User).where(
        User.role.in_([Role.agent, Role.admin]), User.is_active.is_(True), User.id != exclude_id
    )
    return list(db.scalars(query))
