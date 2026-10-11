"""Genera guia-angular-helpdesk.pdf. Uso: py build_guia.py"""
import re
from html import escape
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, CondPageBreak, Frame, KeepTogether, PageBreak, PageTemplate,
                                Paragraph, Preformatted, Spacer, Table, TableStyle)
from reportlab.platypus.tableofcontents import TableOfContents

OUT = Path(__file__).with_name("guia-angular-helpdesk.pdf")
FONTS = Path("C:/Windows/Fonts")
for name, file in [("Sans", "arial.ttf"), ("Sans-B", "arialbd.ttf"), ("Sans-I", "ariali.ttf"),
                   ("Sans-BI", "arialbi.ttf"), ("Mono", "consola.ttf"), ("Mono-B", "consolab.ttf")]:
    pdfmetrics.registerFont(TTFont(name, str(FONTS / file)))
pdfmetrics.registerFontFamily("Sans", normal="Sans", bold="Sans-B", italic="Sans-I", boldItalic="Sans-BI")
pdfmetrics.registerFontFamily("Mono", normal="Mono", bold="Mono-B", italic="Mono", boldItalic="Mono-B")

INK, ACCENT, MUTED = colors.HexColor("#1c1a17"), colors.HexColor("#d9480f"), colors.HexColor("#6b665e")
SOFT, LINE = colors.HexColor("#f6f2ea"), colors.HexColor("#ddd5c6")

S = {
    "body": ParagraphStyle("body", fontName="Sans", fontSize=10, leading=15, textColor=INK, spaceAfter=7),
    "h1": ParagraphStyle("h1", fontName="Sans-B", fontSize=22, leading=26, textColor=INK, spaceAfter=4, keepWithNext=1),
    "h2": ParagraphStyle("h2", fontName="Sans-B", fontSize=13.5, leading=18, textColor=ACCENT, spaceBefore=10, spaceAfter=5,
                           keepWithNext=1),
    "chapno": ParagraphStyle("chapno", fontName="Sans-B", fontSize=9, textColor=ACCENT, spaceAfter=2, keepWithNext=1),
    "bullet": ParagraphStyle("bullet", fontName="Sans", fontSize=10, leading=15, textColor=INK,
                             leftIndent=16, bulletIndent=4, spaceAfter=3),
    "code": ParagraphStyle("code", fontName="Mono", fontSize=8, leading=10.6, textColor=INK, backColor=SOFT,
                           borderColor=LINE, borderWidth=0.6, borderPadding=7, leftIndent=8, rightIndent=8,
                           spaceBefore=6, spaceAfter=14),
    "cell": ParagraphStyle("cell", fontName="Sans", fontSize=8.8, leading=12, textColor=INK),
    "cellh": ParagraphStyle("cellh", fontName="Sans-B", fontSize=8.8, leading=12, textColor=colors.white),
    "cap": ParagraphStyle("cap", fontName="Sans-I", fontSize=8.5, leading=11, textColor=MUTED, spaceAfter=10),
    "toc1": ParagraphStyle("toc1", fontName="Sans", fontSize=11, leading=22, textColor=INK, leftIndent=0),
}


def rich(text: str) -> str:
    """`codigo` -> fuente monoespaciada. El resto del texto usa marcado de ReportLab (<b>, <i>)."""
    return re.sub(r"`([^`]+)`", lambda m: f'<font name="Mono" size="9" color="#b4381a">{escape(m.group(1))}</font>', text)


def P(text, style="body"):
    return Paragraph(rich(text), S[style])


def bullets(*items):
    return [Paragraph(rich(i), S["bullet"], bulletText="•") for i in items]


def code(text):
    return Preformatted(text.strip("\n"), S["code"])


def table(header, rows, widths):
    data = [[Paragraph(rich(h), S["cellh"]) for h in header]] + [[Paragraph(rich(c), S["cell"]) for c in r] for r in rows]
    t = Table(data, colWidths=[w * cm for w in widths], repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), INK), ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, SOFT]), ("GRID", (0, 0), (-1, -1), 0.4, LINE),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return [t, Spacer(1, 12)]


def callout(title, text, color=ACCENT):
    inner = [Paragraph(f"<b>{title}</b>", ParagraphStyle("ct", parent=S["cell"], textColor=color, fontSize=9.5)),
             Paragraph(rich(text), S["cell"])]
    t = Table([[inner]], colWidths=[16.6 * cm])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), SOFT), ("LINEBEFORE", (0, 0), (0, -1), 3, color),
                           ("LEFTPADDING", (0, 0), (-1, -1), 12), ("TOPPADDING", (0, 0), (-1, -1), 8),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 8)]))
    return [KeepTogether(t), Spacer(1, 12)]


class Doc(BaseDocTemplate):
    def afterFlowable(self, f):
        if getattr(f, "_toc", None):
            self.notify("TOCEntry", (0, f._toc, self.page))


def chapter(n, title):
    p = Paragraph(rich(title), S["h1"])
    p._toc = f"{n}. {title}"
    # Salta de página solo si queda poco espacio, para no dejar páginas a medio llenar
    return [Spacer(1, 14), CondPageBreak(9 * cm), Paragraph(f"CAPÍTULO {n}", S["chapno"]), p, Spacer(1, 8)]


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Sans", 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(2 * cm, 1.2 * cm, "Guía de Angular y fundamentos web · Proyecto HelpDesk")
    canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, str(doc.page))
    canvas.restoreState()


story = []

# ---------------------------------------------------------------- Portada
story += [Spacer(1, 5 * cm),
          Paragraph("GUÍA PRÁCTICA", ParagraphStyle("k", parent=S["chapno"], fontSize=11)),
          Paragraph("Angular y fundamentos web", ParagraphStyle("t", fontName="Sans-B", fontSize=34, leading=38, textColor=INK)),
          Spacer(1, 10),
          Paragraph("HTTP, DOM, CSS y métodos GET, POST, PUT, PATCH y DELETE explicados con el código real del proyecto HelpDesk.",
                    ParagraphStyle("s", fontName="Sans", fontSize=14, leading=20, textColor=MUTED)),
          Spacer(1, 2.2 * cm)]
story += table(["Proyecto", "Qué usarás para aprender"], [
    ["<b>HelpDesk</b> (carpeta <font name='Mono'>helpdesk/</font>)", "Angular 22 + FastAPI + PostgreSQL + JWT + roles + correos"],
    ["<b>StoreAPI</b> (carpeta <font name='Mono'>StoreAPI/</font>)", "HTML, CSS y JavaScript puro consumiendo una API pública"],
], [6.6, 10])

# ---------------------------------------------------------------- Índice
toc = TableOfContents()
toc.levelStyles = [S["toc1"]]
story += [PageBreak(), Paragraph("Contenido", S["h1"]), Spacer(1, 10), toc]
story += [Spacer(1, 18)] + callout("Cómo usar esta guía",
    "Cada concepto se explica y luego se muestra <b>dónde aparece en el proyecto</b>. Abre los archivos mencionados, "
    "ejecuta la app y mira la pestaña <b>Network</b> de las herramientas de desarrollo (F12) mientras haces clic: "
    "verás en vivo todo lo que aquí se describe.")

# ---------------------------------------------------------------- 1. La web
story += chapter(1, "Cómo funciona la web")
story += [
    P("Toda aplicación web, sea una tienda o un helpdesk, se reduce a una conversación entre dos programas: el "
      "<b>cliente</b> (tu navegador) y el <b>servidor</b>. El cliente pide cosas y el servidor responde."),
    P("En HelpDesk hay <b>tres</b> piezas hablando entre sí:"),
]
story += table(["Pieza", "Dónde corre", "Responsabilidad"], [
    ["<b>Frontend</b> (Angular)", "En tu navegador, <font name='Mono'>localhost:4200</font>", "Mostrar pantallas y capturar acciones del usuario."],
    ["<b>Backend</b> (FastAPI)", "Contenedor Docker, <font name='Mono'>localhost:8000</font>", "Reglas de negocio, seguridad, validación."],
    ["<b>Base de datos</b> (PostgreSQL)", "Contenedor Docker, red interna", "Guardar usuarios y tickets de forma permanente."],
], [3.8, 5.6, 7.2])
story += [P("El navegador <b>nunca</b> habla directamente con la base de datos. Eso sería un agujero de seguridad: "
            "cualquiera podría leer o borrar todo. El backend es el único guardián."),
          P("Anatomía de una URL", "h2"),
          code("http://localhost:8000/api/tickets?priority=high#top\n"
               "└─┬─┘   └────┬────┘└┬─┘└────┬────┘└────┬──────┘└┬┘\n"
               "protocolo  host   puerto   ruta     query    fragmento"),
          *bullets("<b>Protocolo</b>: <font name='Mono'>http</font> (sin cifrar) o <font name='Mono'>https</font> (cifrado). En producción siempre https.",
                   "<b>Host y puerto</b>: a qué máquina y a qué programa dentro de ella. Por eso HelpDesk usa 4200, 8000 y 8025.",
                   "<b>Ruta</b>: el recurso. <font name='Mono'>/api/tickets</font> significa \"la colección de tickets\".",
                   "<b>Query</b>: filtros opcionales tras el <font name='Mono'>?</font>.",
                   "<b>Fragmento</b>: lo usa solo el navegador; nunca llega al servidor."),
          P("JSON: el idioma de las APIs", "h2"),
          P("Frontend y backend intercambian datos como <b>JSON</b>, un texto con estructura de objetos y listas. "
            "Es lo que devuelve el backend al listar tickets:"),
          code('{ "id": 2, "title": "La impresora no funciona", "priority": "high",\n'
               '  "status": "open", "author": { "id": 3, "name": "Luis" } }'),
          ]

# ---------------------------------------------------------------- 2. HTTP
story += chapter(2, "HTTP: pedir y responder")
story += [
    P("<b>HTTP</b> (HyperText Transfer Protocol) es el \"idioma\" con el que cliente y servidor se entienden. "
      "Es un protocolo de <b>petición y respuesta</b>: el cliente siempre empieza, el servidor nunca habla primero, y "
      "cada par petición/respuesta es independiente (el servidor no \"recuerda\" al cliente; por eso existe el JWT, capítulo 7)."),
    P("Una petición real de HelpDesk", "h2"),
    P("Cuando creas un ticket, Angular envía exactamente esto (puedes verlo en F12 → Network):"),
    code("""POST /api/tickets HTTP/1.1                      ← método + ruta + versión
Host: localhost:8000
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...    ← quién eres (JWT)
Content-Type: application/json                   ← el cuerpo es JSON

{"title":"La impresora no funciona","description":"Atasco","priority":"high"}"""),
    P("Y el servidor responde:"),
    code("""HTTP/1.1 201 Created                             ← código de estado
content-type: application/json
access-control-allow-origin: http://localhost:4200

{"id":2,"title":"La impresora no funciona","status":"open", ...}"""),
    P("Las cuatro partes de un mensaje HTTP", "h2"),
    *bullets("<b>Línea inicial</b>: método y ruta (petición) o código de estado (respuesta).",
             "<b>Cabeceras (headers)</b>: metadatos como <font name='Mono'>Authorization</font>, <font name='Mono'>Content-Type</font> o <font name='Mono'>Origin</font>.",
             "<b>Línea en blanco</b>: separa cabeceras del cuerpo.",
             "<b>Cuerpo (body)</b>: los datos. Las peticiones GET y DELETE normalmente no llevan."),
    P("Códigos de estado que usa el proyecto", "h2"),
    P("El primer dígito dice la familia: <b>2xx</b> éxito, <b>4xx</b> error del cliente, <b>5xx</b> error del servidor."),
]
story += table(["Código", "Significado", "Dónde ocurre en HelpDesk"], [
    ["<b>200</b> OK", "Todo bien, aquí están los datos.", "Listar tickets, hacer login, actualizar un ticket."],
    ["<b>201</b> Created", "Se creó un recurso nuevo.", "Registrarse y crear un ticket."],
    ["<b>204</b> No Content", "Hecho, y no hay nada que devolver.", "Borrar un ticket."],
    ["<b>400</b> Bad Request", "La petición no tiene sentido.", "Un admin intenta modificarse a sí mismo."],
    ["<b>401</b> Unauthorized", "No sabemos quién eres (sin token, vencido o inválido).", "El interceptor cierra la sesión al recibirlo."],
    ["<b>403</b> Forbidden", "Sabemos quién eres, pero no tienes permiso.", "Un <font name='Mono'>user</font> intenta cambiar el estado de un ticket."],
    ["<b>404</b> Not Found", "No existe ese recurso.", "Ticket o usuario con un id inexistente."],
    ["<b>409</b> Conflict", "Choca con algo que ya existe.", "Registrar un email ya usado."],
    ["<b>422</b> Unprocessable", "Los datos no pasan la validación.", "Email mal formado o contraseña de menos de 8 caracteres."],
], [3.3, 6.2, 7.1])
story += callout("401 contra 403: la confusión más común",
                 "<b>401</b> = \"no te conozco\" (autenticación). <b>403</b> = \"te conozco, pero no puedes\" (autorización). "
                 "El frontend reacciona distinto: ante un 401 cierra sesión; ante un 403 solo avisa.")

# ---------------------------------------------------------------- 3. Métodos
story += chapter(3, "Métodos HTTP: GET, POST, PUT, PATCH, DELETE")
story += [
    P("El <b>método</b> indica la <i>intención</i> de la petición. Junto con la ruta forma un patrón llamado <b>API REST</b>: "
      "las rutas son sustantivos (<font name='Mono'>/tickets</font>) y los métodos son los verbos (leer, crear, cambiar, borrar)."),
]
story += table(["Método", "Intención", "¿Seguro?", "¿Idempotente?", "En HelpDesk"], [
    ["<b>GET</b>", "Leer", "Sí", "Sí", "<font name='Mono'>GET /tickets</font>, <font name='Mono'>GET /users</font>"],
    ["<b>POST</b>", "Crear / ejecutar acción", "No", "No", "<font name='Mono'>POST /tickets</font>, <font name='Mono'>POST /auth/login</font>"],
    ["<b>PUT</b>", "Reemplazar completo", "No", "Sí", "No se usa (ver abajo)"],
    ["<b>PATCH</b>", "Modificar parcialmente", "No", "Normalmente sí", "<font name='Mono'>PATCH /tickets/1</font>, <font name='Mono'>PATCH /users/3</font>"],
    ["<b>DELETE</b>", "Borrar", "No", "Sí", "<font name='Mono'>DELETE /tickets/1</font>"],
], [2.0, 3.9, 1.8, 2.7, 6.2])
story += [
    *bullets("<b>Seguro</b>: no cambia nada en el servidor. Por eso el navegador puede repetir un GET sin miedo.",
             "<b>Idempotente</b>: hacerlo 1 o 10 veces deja el servidor igual. Borrar el ticket 1 dos veces: el resultado final es el mismo. "
             "Crear un ticket dos veces: ¡dos tickets! Por eso POST no es idempotente y conviene deshabilitar el botón mientras envía."),
    P("Los cinco, con el código real", "h2"),
    P("Todas las llamadas HTTP del frontend viven en un único archivo, <font name='Mono'>core/api.service.ts</font>:"),
    code("""@Injectable({ providedIn: 'root' })
export class ApiService {
  private http = inject(HttpClient);
  private url = environment.apiUrl;              // http://localhost:8000/api

  tickets() {                                     // GET    → leer
    return this.http.get<Ticket[]>(`${this.url}/tickets`);
  }
  createTicket(data: { title: string; description: string; priority: Priority }) {
    return this.http.post<Ticket>(`${this.url}/tickets`, data);      // POST   → crear
  }
  updateTicketStatus(id: number, status: TicketStatus) {
    return this.http.patch<Ticket>(`${this.url}/tickets/${id}`, { status });  // PATCH
  }
  deleteTicket(id: number) {
    return this.http.delete<void>(`${this.url}/tickets/${id}`);      // DELETE → borrar
  }
}"""),
    P("PUT frente a PATCH", "h2"),
    P("Imagina un ticket con título, descripción, prioridad y estado. Un agente solo quiere pasarlo a \"cerrado\":"),
    code("""PUT   /api/tickets/1   {"title":"...","description":"...","priority":"high","status":"closed"}
      → obliga a reenviar TODOS los campos; los que falten se pierden o se rechazan.

PATCH /api/tickets/1   {"status":"closed"}
      → solo envía lo que cambia. Es lo que usa HelpDesk."""),
    P("Por eso el proyecto usa PATCH: un agente cambia el estado, un admin cambia el rol o la activación de un usuario, "
      "y nadie necesita reenviar el resto. Usa PUT cuando el cliente edita un recurso completo con un formulario."),
    P("El mismo endpoint, visto desde el servidor", "h2"),
    code("""@router.post("", response_model=TicketOut, status_code=201)   # POST /api/tickets → 201
def create_ticket(data: TicketIn, db: DB, user: CurrentUser, background: BackgroundTasks):
    ticket = Ticket(**data.model_dump(), author_id=user.id)    # el autor sale del TOKEN,
    db.add(ticket)                                             # no del cuerpo: no se puede
    db.commit()                                                # suplantar a otra persona
    ..."""),
    *callout("Tu turno: probar los métodos sin Angular",
             "Con el backend corriendo, abre http://localhost:8000/docs. Es una interfaz generada automáticamente donde puedes "
             "ejecutar cada endpoint, ver los códigos de estado y entender el contrato antes de escribir una sola línea de Angular."),
]

# ---------------------------------------------------------------- 4. DOM
story += chapter(4, "HTML y el DOM")
story += [
    P("<b>HTML</b> es el texto que describe la estructura de una página. Cuando el navegador lo lee, construye en memoria "
      "un <b>árbol de objetos</b> llamado <b>DOM</b> (Document Object Model). JavaScript no modifica el texto HTML: "
      "modifica ese árbol, y el navegador repinta lo que cambió."),
    code("""HTML (texto)                    DOM (árbol en memoria)
<main>                          main
  <section id="grid">            └─ section#grid
    <article class="card">           ├─ article.card
      <h3>Camiseta</h3>              │    └─ h3 "Camiseta"
    </article>                       └─ article.card ..."""),
    P("Manipular el DOM a mano: StoreAPI", "h2"),
    P("El proyecto StoreAPI usa JavaScript puro, así que ahí se ve el DOM sin ayuda de ningún framework. "
      "Esta función crea elementos de forma segura:"),
    code("""// StoreAPI/js/main.js
function h(tag, props = {}, ...children) {
    const el = document.createElement(tag);          // 1. crear nodo
    for (const [key, value] of Object.entries(props)) {
        if (key === "class") el.className = value;   // 2. configurar atributos
        else if (key.startsWith("on")) el.addEventListener(key.slice(2), value);
        else el.setAttribute(key, value);
    }
    el.append(...children);                          // 3. colgarle hijos (texto o nodos)
    return el;
}

els.grid.replaceChildren(...list.map(productCard));  // 4. reemplazar el contenido"""),
    *bullets("<font name='Mono'>document.getElementById('grid')</font> / <font name='Mono'>querySelector('.card')</font>: buscan nodos.",
             "<font name='Mono'>createElement</font> + <font name='Mono'>append</font>: construyen nodos nuevos.",
             "<font name='Mono'>addEventListener('click', ...)</font>: reaccionan a lo que hace el usuario.",
             "<font name='Mono'>replaceChildren</font>: reemplaza todo el contenido de un nodo de una vez."),
    P("Eventos y delegación", "h2"),
    P("Cada vez que hay una acción del usuario (clic, teclear, enviar un formulario) el navegador dispara un <b>evento</b>. "
      "Con 20 productos, ¿ponemos 20 escuchadores de clic? No: se pone <b>uno solo</b> en el contenedor, y se averigua qué botón se pulsó. "
      "Es la <b>delegación de eventos</b>:"),
    code("""els.grid.addEventListener("click", (e) => {
    const add = e.target.closest("[data-add]");      // ¿el clic fue en un botón "Agregar"?
    if (add) return addToCart(Number(add.dataset.add));
    const open = e.target.closest("[data-open]");    // ¿o en un producto para ver detalle?
    if (open) openProduct(Number(open.dataset.open));
});"""),
    P("Seguridad: <font name='Mono'>textContent</font> frente a <font name='Mono'>innerHTML</font>", "h2"),
]
story += callout("XSS: el ataque que evita esta decisión",
    "Si un título de producto (o la descripción de un ticket) contiene <font name='Mono'>&lt;script&gt;alert(1)&lt;/script&gt;</font> "
    "y lo insertas con <font name='Mono'>innerHTML</font>, el navegador <b>ejecuta ese código</b>. Con <font name='Mono'>textContent</font> "
    "(que usa <font name='Mono'>h()</font>) se muestra como texto inofensivo. Angular hace esto mismo por ti: <font name='Mono'>{{ t.title }}</font> "
    "siempre escapa el contenido. En HelpDesk lo comprobamos: un ticket con un <font name='Mono'>&lt;script&gt;</font> aparece escapado también en el correo.")
story += [
    P("En Angular el DOM lo gestiona el framework", "h2"),
    P("En el frontend de HelpDesk casi nunca llamas a <font name='Mono'>createElement</font>. Describes cómo debe verse la pantalla "
      "según los datos (la <b>plantilla</b>) y Angular actualiza el DOM por ti cuando los datos cambian. Lo verás en el capítulo 6."),
]

# ---------------------------------------------------------------- 5. CSS
story += chapter(5, "CSS: los estilos")
story += [
    P("HTML dice <i>qué</i> es cada cosa; <b>CSS</b> dice <i>cómo se ve</i>. Una regla CSS tiene un <b>selector</b> "
      "(a quién) y declaraciones (qué cambiar):"),
    code(""".chip {                       /* selector: todo elemento con class="chip" */
    padding: 8px 16px;         /* propiedad: valor; */
    border-radius: 999px;      /* esquinas totalmente redondeadas */
}
.chip[aria-pressed="true"] {   /* selector de atributo: solo el chip activo */
    background: var(--ink);
    color: #fff;
}"""),
    P("Selectores más usados", "h2"),
]
story += table(["Selector", "Elige", "Ejemplo en el proyecto"], [
    ["<font name='Mono'>p</font>", "Por etiqueta", "<font name='Mono'>button { cursor: pointer; }</font>"],
    ["<font name='Mono'>.clase</font>", "Por clase", "<font name='Mono'>.card</font>, <font name='Mono'>.badge</font>, <font name='Mono'>.error</font>"],
    ["<font name='Mono'>#id</font>", "Por id (único)", "Poco usado: tiene demasiado peso"],
    ["<font name='Mono'>a b</font>", "Descendiente", "<font name='Mono'>header a</font> (enlaces dentro del header)"],
    ["<font name='Mono'>a:hover</font>", "Estado del ratón", "<font name='Mono'>.card:hover</font> eleva la tarjeta"],
    ["<font name='Mono'>[attr]</font>", "Por atributo", "<font name='Mono'>.cart-count[hidden]</font>"],
], [3.3, 4.0, 9.3])
story += [
    P("La cascada y la especificidad", "h2"),
    P("\"Cascading\" significa que varias reglas pueden aplicar al mismo elemento y hay un orden para decidir quién gana: "
      "1) la más <b>específica</b> (un id pesa más que una clase y una clase más que una etiqueta) y 2) a igual especificidad, la que viene <b>después</b>."),
]
story += callout("Un bug real que ocurrió en este proyecto",
    "En StoreAPI el contador del carrito se veía como un punto naranja aunque estuviera vacío. El HTML tenía <font name='Mono'>hidden</font> "
    "(que el navegador traduce a <font name='Mono'>display:none</font>), pero mi regla <font name='Mono'>.cart-count { display: grid }</font> "
    "tenía más prioridad y lo anulaba. La solución fue una regla más específica: <font name='Mono'>.cart-count[hidden] { display: none; }</font>.", ACCENT)
story += [
    P("El modelo de caja", "h2"),
    P("Todo elemento es una caja con cuatro capas, de dentro hacia fuera: <b>contenido → padding → borde → margin</b>. "
      "Por eso el proyecto empieza con <font name='Mono'>* { box-sizing: border-box; }</font>: así el ancho incluye padding y borde y las cuentas salen como esperas."),
    P("Maquetación moderna: Flexbox y Grid", "h2"),
    code("""/* Flexbox: una dimensión (fila o columna). Ideal para barras y grupos de botones. */
header { display: flex; align-items: center; gap: 24px; }

/* Grid: dos dimensiones. Aquí: tantas columnas de mínimo 240px como quepan. */
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 24px; }"""),
    P("Esa única línea del <font name='Mono'>.grid</font> hace que la tienda tenga 4 columnas en escritorio, 2 en tablet y 1 en móvil pequeño, sin escribir un solo cálculo."),
    P("Variables CSS y diseño adaptable", "h2"),
    code(""":root {                                  /* se define una vez ... */
    --accent: #e4572e;
    --radius: 16px;
}
.btn.primary { background: var(--accent); }   /* ... y se usa en todos lados */

@media (max-width: 680px) {              /* media query: reglas solo en pantallas pequeñas */
    .grid { grid-template-columns: repeat(2, 1fr); }
}"""),
    P("Cambiar <font name='Mono'>--accent</font> recolorea toda la tienda. Y con la media query la página se adapta al móvil: eso es <b>diseño responsivo</b>."),
    P("Estilos en Angular", "h2"),
    P("En HelpDesk hay dos niveles: <font name='Mono'>src/styles.css</font> (estilos <b>globales</b>, como <font name='Mono'>.card</font> o <font name='Mono'>.badge</font>) "
      "y <font name='Mono'>app.css</font> (estilos <b>del componente</b>). Angular encapsula los de componente para que no se filtren al resto de la página."),
]

# ---------------------------------------------------------------- 6. Angular
story += chapter(6, "Angular paso a paso")
story += [
    P("<b>Angular</b> es un framework para construir la parte visible de una aplicación (el frontend). Resuelve lo que en StoreAPI "
      "hacíamos a mano: mantener el DOM sincronizado con los datos, organizar el código y navegar entre pantallas sin recargar."),
    P("Estructura del proyecto", "h2"),
    code("""frontend/src/
├── main.ts                       ← arranque: bootstrapApplication(App, appConfig)
├── styles.css                    ← estilos globales (compartidos)
├── environments/environment.ts   ← apiUrl: 'http://localhost:8000/api'
└── app/
    ├── app.ts / .html / .css / .spec.ts   ← componente raíz: barra de navegación + <router-outlet>
    ├── app.config.ts             ← configuración: router, HttpClient, interceptor
    ├── app.routes.ts             ← mapa de rutas (qué URL muestra qué pantalla)
    ├── core/                     ← lógica compartida (cada archivo con su .spec.ts)
    │   ├── auth.service.ts       ← sesión, login, registro, token
    │   ├── api.service.ts        ← TODAS las llamadas HTTP de tickets y usuarios
    │   ├── auth-interceptor.ts   ← añade el JWT a cada petición
    │   ├── auth-guard.ts         ← protege rutas: exige sesión iniciada
    │   ├── role-guard.ts         ← protege rutas: exige un rol concreto
    │   └── models.ts             ← tipos: User, Ticket, Role ...
    └── pages/                    ← una carpeta por pantalla
        ├── login/    login.ts  login.html  login.css  login.spec.ts
        ├── register/ register.ts ... (los mismos 4 archivos)
        ├── tickets/  tickets.ts ...
        └── users/    users.ts ..."""),
    P("1. Componentes: cuatro archivos por pantalla", "h2"),
    P("Un <b>componente</b> es un trozo de interfaz reutilizable. Angular lo separa en cuatro archivos con el mismo nombre, "
      "cada uno con una sola responsabilidad. No se escriben a mano: los crea el CLI."),
    code("""ng generate component pages/login        # crea la carpeta pages/login/ con:

login.ts        ← la CLASE: datos y comportamiento (TypeScript)
login.html      ← la PLANTILLA: qué se dibuja (HTML + sintaxis de Angular)
login.css       ← los ESTILOS: solo de este componente (Angular los encapsula)
login.spec.ts   ← las PRUEBAS automáticas del componente"""),
    P("El decorador <font name='Mono'>@Component</font> conecta los tres primeros. Resumen de <font name='Mono'>pages/login/login.ts</font>:"),
    code("""@Component({
  imports: [FormsModule, RouterLink],     // lo que la plantilla puede usar
  selector: 'app-login',                  // etiqueta HTML del componente
  styleUrl: './login.css',                // → los estilos
  templateUrl: './login.html',            // → la plantilla
})
export class Login {
  email = '';
  password = '';
  loading = signal(false);
  error = signal('');
  submit() { ... }
}"""),
    P("Y un extracto de <font name='Mono'>pages/login/login.html</font>, donde viven los enlaces con la clase:"),
    code("""<form (ngSubmit)="submit()">                         <!-- evento: al enviar, llama a submit() -->
  <input type="email" name="email" [(ngModel)]="email" required />   <!-- enlace de datos -->
  @if (error()) { <p class="error">{{ error() }}</p> }               <!-- condicional -->
  <button [disabled]="loading()">Entrar</button>
</form>"""),
    P("Los estilos que solo usa esta pantalla van en <font name='Mono'>login.css</font> (por ejemplo, el ancho de la tarjeta). "
      "Lo que comparten todas las pantallas (botones, tarjetas, tablas) queda en el <font name='Mono'>styles.css</font> global."),
    P("2. Enlace de datos (data binding)", "h2"),
]
story += table(["Sintaxis", "Dirección", "Qué hace", "Ejemplo"], [
    ["<font name='Mono'>{{ valor }}</font>", "Clase → vista", "Muestra un dato como texto (escapado).", "<font name='Mono'>{{ t.title }}</font>"],
    ["<font name='Mono'>[propiedad]=\"x\"</font>", "Clase → vista", "Asigna una propiedad del elemento.", "<font name='Mono'>[disabled]=\"loading()\"</font>"],
    ["<font name='Mono'>(evento)=\"f()\"</font>", "Vista → clase", "Reacciona a un evento del DOM.", "<font name='Mono'>(click)=\"auth.logout()\"</font>"],
    ["<font name='Mono'>[(ngModel)]=\"x\"</font>", "Ambas", "Sincroniza un campo de formulario con una variable.", "<font name='Mono'>[(ngModel)]=\"email\"</font>"],
], [3.9, 2.7, 5.5, 4.5])
story += [
    P("3. Control de flujo en plantillas: <font name='Mono'>@if</font> y <font name='Mono'>@for</font>", "h2"),
    code("""@if (auth.hasRole('admin')) {                 <!-- solo el admin ve el enlace -->
  <a routerLink="/users">Usuarios</a>
}

@for (t of tickets(); track t.id) {          <!-- repite la fila por cada ticket -->
  <tr><td>{{ t.title }}</td> ...</tr>
} @empty {
  <tr><td colspan="7">No hay tickets.</td></tr>
}"""),
    P("<font name='Mono'>track t.id</font> le dice a Angular cómo identificar cada fila, así al cambiar la lista solo toca las filas afectadas en el DOM en lugar de rehacer todo."),
    P("4. Signals: datos que avisan cuando cambian", "h2"),
    P("Un <b>signal</b> es una caja que guarda un valor y notifica a la plantilla cuando cambia. Se lee como una función (<font name='Mono'>tickets()</font>) y se modifica con <font name='Mono'>set</font> o <font name='Mono'>update</font>:"),
    code("""tickets = signal<Ticket[]>([]);

this.tickets.set(listaDelServidor);                                    // reemplaza
this.tickets.update((list) => [nuevoTicket, ...list]);                // al crear: lo agrega primero
this.tickets.update((list) => list.filter((x) => x.id !== t.id));     // al borrar: lo quita

readonly isLoggedIn = computed(() => !!this.token() && !!this.user()); // derivado automático"""),
    P("Cuando haces <font name='Mono'>update</font>, Angular repinta únicamente lo que depende de ese signal. Ese es el equivalente automático de lo que hacía <font name='Mono'>replaceChildren</font> en StoreAPI."),
    P("5. Servicios e inyección de dependencias", "h2"),
    P("La lógica que no pertenece a una pantalla concreta (sesión, llamadas HTTP) va en <b>servicios</b>. Un componente los pide con <font name='Mono'>inject()</font> y Angular le entrega "
      "<b>una única instancia compartida</b> (<font name='Mono'>providedIn: 'root'</font>):"),
    code("""export class Tickets {
  private api = inject(ApiService);        // "dame el ApiService"
  protected auth = inject(AuthService);    // "dame el AuthService": es el mismo en toda la app
  ..."""),
    P("Gracias a eso, cuando <font name='Mono'>Login</font> guarda el usuario en <font name='Mono'>AuthService</font>, la barra de navegación (otro componente) lo ve al instante."),
    P("6. HttpClient y Observables", "h2"),
    P("Las llamadas de red son <b>asíncronas</b>: la respuesta tarda y la pantalla no puede congelarse esperando. "
      "<font name='Mono'>HttpClient</font> devuelve un <b>Observable</b>: una promesa de datos futuros. <b>Nada se envía hasta que alguien hace <font name='Mono'>subscribe</font></b>:"),
    code("""create() {
  this.api.createTicket({ title: this.title, description: this.description,
                          priority: this.priority })
    .subscribe({
      next:  (t)  => this.tickets.update((list) => [t, ...list]),   // llegó 201
      error: ()   => this.error.set('No se pudo crear el ticket'),  // llegó 4xx/5xx
    });
}"""),
    P("7. El enrutador y la carga diferida", "h2"),
    code("""export const routes: Routes = [
  { path: 'login',   loadComponent: () => import('./pages/login/login').then((m) => m.Login) },
  { path: 'tickets', canActivate: [authGuard],
                     loadComponent: () => import('./pages/tickets/tickets').then((m) => m.Tickets) },
  { path: 'users',   canActivate: [roleGuard('admin')],
                     loadComponent: () => import('./pages/users/users').then((m) => m.Users) },
  { path: '**', redirectTo: 'tickets' },
];"""),
    *bullets("<b>Router</b>: cambia la \"pantalla\" según la URL, sin recargar la página (es una <i>SPA</i>, Single Page Application).",
             "<b>loadComponent con import()</b>: el código de cada pantalla se descarga solo cuando entras (<i>lazy loading</i>). Por eso al compilar vimos <i>chunks</i> separados: login, tickets, users.",
             "<b>canActivate</b>: los <i>guards</i> deciden si puedes entrar. Si no, te redirigen."),
    P("8. Guards", "h2"),
    code("""// core/auth-guard.ts
export const authGuard: CanActivateFn = () => {
  const auth = inject(AuthService);
  return auth.isLoggedIn() || inject(Router).createUrlTree(['/login']);  // true, o redirige
};

// core/role-guard.ts  (una "fábrica": recibe los roles permitidos)
export const roleGuard = (...roles: Role[]): CanActivateFn => () => { ... };"""),
]
story += callout("Los guards NO son seguridad",
    "Un guard solo mejora la experiencia: oculta pantallas a quien no corresponden. Cualquier usuario puede modificar el JavaScript de su navegador "
    "o llamar a la API directamente. <b>La seguridad real está en el backend</b>, que valida el token y el rol en cada endpoint (capítulo 7).", ACCENT)

story += [
    P("9. Pruebas automáticas: el archivo <font name='Mono'>.spec.ts</font>", "h2"),
    P("Cada pieza tiene junto a ella su <font name='Mono'>.spec.ts</font> (lo genera el CLI). Son programas que ejecutan tu código y comprueban "
      "que hace lo esperado, sin abrir el navegador ni llamar al backend real. HelpDesk las ejecuta con <b>Vitest</b>:"),
    code("""ng test                    # modo interactivo, se repite al guardar
ng test --watch=false      # una sola pasada (útil antes de entregar)"""),
    P("La clave para probar HTTP es <font name='Mono'>HttpTestingController</font>: intercepta las peticiones, te deja revisarlas "
      "(método, URL, cuerpo) y tú decides qué respuesta simular. Así se prueba el PATCH del cambio de estado sin servidor:"),
    code("""it('setStatus() sends a PATCH and updates the row', () => {
  component.setStatus(ticket, 'closed');

  const req = http.expectOne(`${url}/1`);              // ¿salió UNA petición a esta URL?
  expect(req.request.method).toBe('PATCH');            // ¿con el método correcto?
  expect(req.request.body).toEqual({ status: 'closed' });  // ¿y solo con lo que cambia?

  req.flush({ ...ticket, status: 'closed' });          // simulamos la respuesta 200
  expect(component.tickets()[0].status).toBe('closed');    // la pantalla se actualizó
});"""),
    P("Las pruebas de HelpDesk también protegen reglas de negocio: que un <font name='Mono'>user</font> no vea el botón de borrar, que el interceptor "
      "cierre sesión con un 401 pero <b>no</b> con un 403, o que un JWT vencido se descarte al abrir la app."),
]

# ---------------------------------------------------------------- 7. JWT
story += chapter(7, "Autenticación: JWT, interceptor y roles")
story += [
    P("Como HTTP no recuerda quién eres entre una petición y la siguiente, hay que demostrar tu identidad <b>en cada una</b>. "
      "Para eso el servidor te entrega, al iniciar sesión, un <b>JWT</b> (JSON Web Token): un carnet firmado."),
    P("Anatomía de un JWT", "h2"),
    code("""eyJhbGciOiJIUzI1NiIs...  .  eyJzdWIiOiIzIiwiZXhwIjoxNzkx...  .  Uod30wg4aPepQg9Q...
└──── cabecera ─────────┘     └────── contenido (payload) ───────┘     └──── firma ────┘
{ "alg": "HS256" }             { "sub": "3", "exp": 1791649468 }        HMAC con SECRET_KEY"""),
    *bullets("<font name='Mono'>sub</font>: el id del usuario. <font name='Mono'>exp</font>: cuándo vence.",
             "La <b>firma</b> se calcula con una clave que solo conoce el servidor. Si alguien cambia el contenido, la firma deja de coincidir y el servidor lo rechaza.",
             "El contenido está codificado, <b>no cifrado</b>: cualquiera puede leerlo. Nunca pongas contraseñas ahí."),
    P("El flujo completo", "h2"),
    code("""1. POST /auth/login {email, password}      →  servidor verifica con bcrypt
2. 200 {access_token, user}                ←  servidor firma un JWT
3. Angular guarda el token (localStorage) y el usuario (signal)
4. Cada petición siguiente lleva:  Authorization: Bearer <token>
5. FastAPI valida firma + vencimiento, busca al usuario, y comprueba su rol"""),
    P("El interceptor: añadir el token una sola vez", "h2"),
    P("En lugar de acordarse de poner la cabecera en cada llamada, un <b>interceptor</b> se interpone en <i>todas</i> las peticiones salientes:"),
    code("""export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const auth = inject(AuthService);
  const token = auth.token();
  if (token) req = req.clone({ setHeaders: { Authorization: `Bearer ${token}` } });

  return next(req).pipe(
    catchError((err) => {
      if (err.status === 401 && token) auth.logout();   // token vencido: cerrar sesión
      return throwError(() => err);
    }),
  );
};"""),
    P("Roles: dos niveles de protección", "h2"),
]
story += table(["Rol", "Puede", "Capa que lo impide"], [
    ["<b>user</b>", "Crear tickets y ver solo los suyos.", "Backend: <font name='Mono'>if user.role == Role.user: query.where(author_id == user.id)</font>"],
    ["<b>agent</b>", "Ver todos los tickets y cambiar su estado.", "Backend: <font name='Mono'>require_roles(agent, admin)</font> → 403 si no"],
    ["<b>admin</b>", "Todo, incluido borrar tickets y gestionar usuarios.", "Backend: <font name='Mono'>require_roles(admin)</font>"],
], [2.2, 6.0, 8.4])
story += [
    code("""# backend/app/deps.py
def require_roles(*roles: Role):
    def checker(user: CurrentUser) -> User:
        if user.role not in roles:
            raise HTTPException(403, "No tienes permisos para esta acción")
        return user
    return checker"""),
    P("Detalle de diseño: el JWT guarda <b>solo el id</b>, no el rol. En cada petición el servidor lee el rol actual de la base de datos. "
      "Así, si un admin degrada o desactiva a alguien, el cambio surte efecto de inmediato en lugar de esperar a que venza el token."),
    P("CORS: por qué aparecen peticiones OPTIONS", "h2"),
    P("El navegador aplica la <b>política del mismo origen</b>: una página en <font name='Mono'>localhost:4200</font> no puede leer respuestas de "
      "<font name='Mono'>localhost:8000</font> a menos que ese servidor lo autorice (puerto distinto = origen distinto). Para una petición con "
      "cabecera <font name='Mono'>Authorization</font>, el navegador primero envía por su cuenta un <b>preflight</b>:"),
    code("""OPTIONS /api/tickets                        ← "¿me dejas hacer esto desde 4200?"
Origin: http://localhost:4200
Access-Control-Request-Headers: authorization

200 OK
access-control-allow-origin: http://localhost:4200    ← "sí"  → ahora sí viaja el GET/POST real"""),
    P("Esto lo vimos en el log del servidor: cada acción del frontend aparece precedida de un <font name='Mono'>OPTIONS</font>. "
      "Se configura en <font name='Mono'>main.py</font> con <font name='Mono'>CORSMiddleware</font> y la variable <font name='Mono'>CORS_ORIGINS</font>."),
]

# ---------------------------------------------------------------- 8. Flujo
story += chapter(8, "Todo junto: la vida de un clic")
story += [
    P("Sigamos exactamente qué ocurre cuando un usuario pulsa <b>\"Crear ticket\"</b>. Cada paso usa un concepto de los capítulos anteriores."),
]
story += table(["#", "Qué pasa", "Concepto"], [
    ["1", "El usuario rellena el formulario. <font name='Mono'>[(ngModel)]</font> copia cada tecla a las variables <font name='Mono'>title</font> y <font name='Mono'>description</font>.", "Enlace de datos, DOM"],
    ["2", "Pulsa el botón: el navegador lanza el evento <font name='Mono'>submit</font>; Angular ejecuta <font name='Mono'>create()</font>.", "Eventos"],
    ["3", "<font name='Mono'>ApiService.createTicket()</font> prepara un <font name='Mono'>POST</font>. Aún no se envía.", "Observable, método POST"],
    ["4", "<font name='Mono'>.subscribe()</font> lo dispara. El interceptor añade <font name='Mono'>Authorization: Bearer ...</font>.", "Interceptor, JWT"],
    ["5", "El navegador envía un <font name='Mono'>OPTIONS</font> (preflight) y, si lo aprueban, el <font name='Mono'>POST</font> real.", "HTTP, CORS"],
    ["6", "FastAPI valida el token, busca al usuario y comprueba que está activo.", "401 si falla"],
    ["7", "Pydantic valida el cuerpo (<font name='Mono'>TicketIn</font>): título no vacío, prioridad válida.", "422 si falla"],
    ["8", "Se guarda el ticket en PostgreSQL y se encolan los correos (autor + agentes) en segundo plano.", "Base de datos, Mailpit"],
    ["9", "El servidor responde <font name='Mono'>201 Created</font> con el ticket en JSON.", "Código de estado"],
    ["10", "<font name='Mono'>next</font> se ejecuta: <font name='Mono'>tickets.update(...)</font> añade el ticket al signal.", "Signals"],
    ["11", "Angular detecta el cambio, ejecuta de nuevo el <font name='Mono'>@for</font> y actualiza solo las filas necesarias del DOM.", "DOM, plantillas"],
    ["12", "El navegador repinta la pantalla aplicando las reglas CSS. El usuario ve su ticket en la lista.", "CSS"],
], [0.9, 11.3, 4.4])
story += [
    P("Cómo verlo con tus propios ojos", "h2"),
    *bullets("Abre HelpDesk, pulsa <b>F12</b> y ve a la pestaña <b>Network</b>.",
             "Crea un ticket y localiza el <font name='Mono'>POST tickets</font>. Revisa <b>Headers</b> (verás el Bearer), <b>Payload</b> (el JSON enviado) y <b>Response</b> (el 201).",
             "En <b>Elements</b> inspecciona la fila nueva: es el DOM real que Angular generó.",
             "Abre http://localhost:8025 (Mailpit): ahí están los correos que disparó ese mismo POST."),
]

# ---------------------------------------------------------------- 9. Ejercicios
story += chapter(9, "Ejercicios y glosario")
story += [
    P("Ejercicios sugeridos (de menor a mayor dificultad)", "h2"),
    *bullets("<b>GET con filtros</b>: añade en la pantalla de tickets un <font name='Mono'>&lt;select&gt;</font> para filtrar por estado. Primero hazlo en el cliente con un <font name='Mono'>computed</font>; luego pásalo al servidor con <font name='Mono'>?status=open</font>.",
             "<b>CSS</b>: en HelpDesk, cambia el color de acento por una variable CSS (<font name='Mono'>:root { --accent }</font>) como en StoreAPI y úsala en botones y enlaces.",
             "<b>DELETE</b>: añade el botón \"Borrar\" también para el autor de un ticket que siga abierto. Decide en el backend qué código devuelves si un usuario intenta borrar el de otro (¿403 o 404?).",
             "<b>PUT</b>: crea <font name='Mono'>PUT /tickets/{id}</font> para que un usuario edite título y descripción de su ticket abierto, con formulario en Angular. Compara con el PATCH.",
             "<b>Interceptor</b>: crea otro con <font name='Mono'>ng generate interceptor core/loading</font> que muestre un indicador de \"cargando\" mientras haya peticiones en curso, y escribe su <font name='Mono'>.spec.ts</font>.",
             "<b>Seguridad</b>: desde la consola del navegador, intenta llamar a <font name='Mono'>DELETE /api/tickets/1</font> con el token de un usuario normal y verifica que el servidor responde 403 aunque el botón esté oculto."),
    P("Glosario rápido", "h2"),
]
story += table(["Término", "Significado"], [
    ["API", "Contrato de rutas y datos por el que dos programas se comunican."],
    ["REST", "Estilo de API: rutas como sustantivos y métodos HTTP como verbos."],
    ["Endpoint", "Una combinación concreta de método y ruta, por ejemplo <font name='Mono'>POST /api/tickets</font>."],
    ["DOM", "Árbol en memoria que representa la página; JavaScript lo manipula."],
    ["SPA", "Aplicación de una sola página: cambia pantallas sin recargar el navegador."],
    ["Componente", "Pieza de interfaz = clase TypeScript + plantilla HTML (+ estilos)."],
    ["Signal", "Valor reactivo que avisa a la plantilla cuando cambia."],
    ["Observable", "Flujo de datos asíncrono; no se ejecuta hasta hacer <font name='Mono'>subscribe</font>."],
    ["Interceptor", "Código que se ejecuta en cada petición o respuesta HTTP."],
    ["Guard", "Función que decide si una ruta puede activarse."],
    ["JWT", "Token firmado que prueba la identidad en cada petición."],
    ["CORS", "Mecanismo por el que un servidor autoriza a páginas de otro origen."],
    ["Idempotente", "Repetir la operación no cambia el resultado final."],
    ["XSS", "Inyección de código a través de contenido no escapado."],
    ["Preflight", "Petición OPTIONS que el navegador envía antes de una petición CORS."],
], [3.3, 13.3])
story += callout("Siguiente paso",
    "Cambia algo pequeño, rompe algo a propósito y mira qué dice la pestaña Network y la consola. "
    "Entender los errores (un 401, un 422, un fallo de CORS) enseña más que cualquier lectura.", ACCENT)

# ---------------------------------------------------------------- Build
doc = Doc(str(OUT), pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm, topMargin=2 * cm, bottomMargin=2 * cm,
          title="Guía de Angular y fundamentos web — Proyecto HelpDesk", author="HelpDesk")
frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="f")
doc.addPageTemplates([PageTemplate(id="p", frames=[frame], onPage=footer)])
doc.multiBuild(story)
print("OK ->", OUT)
