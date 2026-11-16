"""Génération dynamique d'un catalogue PDF à partir des livres en base. Usage de ChatGPT en 2024, et Mistral-AI en 2026."""

import os
from datetime import date
from typing import Optional
from uuid import uuid4
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (
    HRFlowable,
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

try:
    from database.commands import session_commands
    from database.models.models import Book
except ModuleNotFoundError:
    from app.packages.database.commands import session_commands
    from app.packages.database.models.models import Book


# Variable globale conservée pour pouvoir être mockée pendant les tests.
DUMMY_IMAGE_PATH = os.getenv("PDF_BRAND_IMAGE", "dummy-ops.png")

PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 18 * mm
HEADER_HEIGHT = 24 * mm
FOOTER_HEIGHT = 16 * mm
BOOK_IMAGE_SIZE = 42 * mm

COLOR_PRIMARY = colors.HexColor("#1F3864")
COLOR_ACCENT = colors.HexColor("#2E74B5")
COLOR_TEXT = colors.HexColor("#222222")
COLOR_MUTED = colors.HexColor("#555555")
COLOR_ROW_BG = colors.HexColor("#F4F7FB")
COLOR_BORDER = colors.HexColor("#C9D4E4")

STYLES = {
    "cover_title": ParagraphStyle(
        "CoverTitle", fontName="Helvetica-Bold", fontSize=30, leading=36,
        textColor=COLOR_PRIMARY, alignment=TA_CENTER,
    ),
    "cover_sub": ParagraphStyle(
        "CoverSub", fontName="Helvetica", fontSize=12, leading=16,
        textColor=COLOR_MUTED, alignment=TA_CENTER,
    ),
    "book_title": ParagraphStyle(
        "BookTitle", fontName="Helvetica-Bold", fontSize=13, leading=16,
        textColor=COLOR_PRIMARY, spaceAfter=2,
    ),
    "book_meta": ParagraphStyle(
        "BookMeta", fontName="Helvetica", fontSize=9.5, leading=13,
        textColor=COLOR_MUTED,
    ),
    "book_summary": ParagraphStyle(
        "BookSummary", fontName="Helvetica", fontSize=10, leading=14,
        textColor=COLOR_TEXT, alignment=TA_JUSTIFY, spaceBefore=4,
    ),
    "placeholder": ParagraphStyle(
        "Placeholder", fontName="Helvetica-Oblique", fontSize=9, leading=12,
        textColor=COLOR_MUTED, alignment=TA_CENTER,
    ),
}


def _env(name: str, default: str) -> str:
    value = os.getenv(name)
    return value if value else default


def get_the_books_list_from_postgresql() -> list:
    """Retourne la liste des livres (dictionnaires) depuis la base PostgreSQL."""
    session = session_commands.get_a_database_session()
    try:
        all_books = session.query(Book).order_by(Book.id).all()
        return [book.get_json_for_pdf(session) for book in all_books]
    finally:
        session.close()


def resolve_book_image_path(file_name) -> Optional[str]:
    """Résout le chemin d'une image de livre en bloquant toute sortie du dossier autorisé."""
    if not file_name:
        return None
    base_dir = os.path.realpath(_env("BOOKS_IMAGE_DIR", "/home/dummy-operator/staticfiles/img"))
    candidate = os.path.realpath(os.path.join(base_dir, os.path.basename(str(file_name))))
    try:
        if os.path.commonpath([base_dir, candidate]) != base_dir:
            return None
    except ValueError:
        return None
    return candidate if os.path.isfile(candidate) else None


def build_output_pdf_path() -> str:
    """Construit un chemin de sortie sûr (dossier créé si besoin, nom assaini)."""
    folder = os.path.abspath(_env("PDF_FOLDER_PATH", "pdf_output"))
    os.makedirs(folder, exist_ok=True)
    base_name = os.path.basename(_env("PDF_FILE_NAME", "catalogue")) or "catalogue"
    return os.path.join(folder, f"{base_name}-{uuid4()}.pdf")


def _image_size(path: str) -> Optional[tuple]:
    try:
        width, height = ImageReader(path).getSize()
    except Exception:
        return None
    if width <= 0 or height <= 0:
        return None
    return width, height


def make_book_image(path: str) -> Optional[Image]:
    size = _image_size(path)
    if size is None:
        return None
    width, height = size
    scale = min(BOOK_IMAGE_SIZE / width, BOOK_IMAGE_SIZE / height)
    return Image(path, width=width * scale, height=height * scale)


def book_block(book: dict):
    """Construit le bloc visuel d'un livre : image à gauche, informations à droite."""
    image_path = resolve_book_image_path(book.get("book_picture_name"))
    image = make_book_image(image_path) if image_path else None
    if image is None:
        image = Paragraph("Image indisponible", STYLES["placeholder"])

    title = escape(str(book.get("title") or "Titre inconnu"))
    details = [Paragraph(f"<b>{title}</b>", STYLES["book_title"])]
    for label, key in (
        ("Auteur", "author"),
        ("Catégorie", "category"),
        ("Année de publication", "year_of_publication"),
        ("Date de publication", "publication_date"),
    ):
        value = book.get(key)
        if value not in (None, ""):
            details.append(Paragraph(f"<b>{label} :</b> {escape(str(value))}", STYLES["book_meta"]))
    summary = book.get("summary") or ""
    content = book.get("content") or ""
    if summary:
        details.append(Paragraph(escape(str(summary)), STYLES["book_summary"]))
    if content:
        details.append(Paragraph(escape(str(content)), STYLES["book_meta"]))
        

    table = Table([[image, details]], colWidths=[BOOK_IMAGE_SIZE + 10 * mm, None])
    table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BACKGROUND", (0, 0), (-1, -1), COLOR_ROW_BG),
        ("BOX", (0, 0), (-1, -1), 0.6, COLOR_BORDER),
        ("LINEBEFORE", (0, 0), (0, -1), 3, COLOR_ACCENT),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    return KeepTogether([table, Spacer(1, 6 * mm)])


def _draw_fitted_image(c, path: str, x: float, y: float, max_width: float, max_height: float) -> bool:
    """Dessine une image ajustée (ratio conservé, centrée) dans un cadre donné."""
    size = _image_size(path)
    if size is None:
        return False
    width, height = size
    scale = min(max_width / width, max_height / height)
    draw_width, draw_height = width * scale, height * scale
    c.drawImage(
        path,
        x + (max_width - draw_width) / 2,
        y + (max_height - draw_height) / 2,
        width=draw_width,
        height=draw_height,
        mask="auto",
    )
    return True


def draw_page_decorations(c, doc) -> None:
    """Dessine l'en-tête et le pied de page (avec numéro de page) sur chaque page."""
    c.saveState()
    brand_image = _env("PDF_BRAND_IMAGE", DUMMY_IMAGE_PATH)
    if os.path.isfile(brand_image):
        _draw_fitted_image(
            c, brand_image, MARGIN, PAGE_HEIGHT - HEADER_HEIGHT,
            PAGE_WIDTH - 2 * MARGIN, HEADER_HEIGHT,
        )
    else:
        c.setFillColor(COLOR_PRIMARY)
        c.rect(0, PAGE_HEIGHT - 12 * mm, PAGE_WIDTH, 12 * mm, stroke=0, fill=1)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(MARGIN, PAGE_HEIGHT - 8.5 * mm, "Lectures")

    c.setStrokeColor(COLOR_BORDER)
    c.setLineWidth(0.6)
    c.line(MARGIN, FOOTER_HEIGHT + 4 * mm, PAGE_WIDTH - MARGIN, FOOTER_HEIGHT + 4 * mm)
    if os.path.isfile(brand_image):
        _draw_fitted_image(c, brand_image, MARGIN, 4 * mm, 26 * mm, FOOTER_HEIGHT - 4 * mm)
    c.setFillColor(COLOR_MUTED)
    c.setFont("Helvetica", 9)
    c.drawRightString(PAGE_WIDTH - MARGIN, 6.5 * mm, f"Page {doc.page}")
    c.restoreState()


def cover_flowables(book_count: int) -> list:
    """Construit la page de couverture du catalogue."""
    return [
        Spacer(1, 45 * mm),
        Paragraph("Lectures", STYLES["cover_title"]),
        Spacer(1, 6 * mm),
        HRFlowable(width="40%", thickness=1, color=COLOR_ACCENT, hAlign="CENTER"),
        Spacer(1, 6 * mm),
        Paragraph(f"{book_count} ouvrage(s)", STYLES["cover_sub"]),
        Spacer(1, 4 * mm),
        Paragraph(f"Édité le {date.today().strftime('%d/%m/%Y')}", STYLES["cover_sub"]),
        PageBreak(),
    ]


def generate_a_pdf_to_consume() -> str:
    """Génère le catalogue PDF et retourne le chemin du fichier créé."""
    books_list = get_the_books_list_from_postgresql()
    pdf_file_path = build_output_pdf_path()

    doc = SimpleDocTemplate(
        pdf_file_path,
        pagesize=A4,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=HEADER_HEIGHT + 8 * mm,
        bottomMargin=FOOTER_HEIGHT + 8 * mm,
        title="Catalogue",
        author="Catalogue",
        subject="Catalogue des livres",
    )

    story = cover_flowables(len(books_list))
    for book in books_list:
        story.append(book_block(book))

    doc.build(story, onFirstPage=lambda c, d: None, onLaterPages=draw_page_decorations)
    return pdf_file_path