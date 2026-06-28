from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A6
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import Image as RLImage
from pathlib import Path
import os
from app.core.config import settings


def generate_id_card_pdf(student_data: dict) -> str:
    """
    Generate a professional PDF ID card for a student.
    Returns the relative path to the saved PDF.
    """
    storage_dir = Path(settings.STORAGE_PATH) / "idcards"
    storage_dir.mkdir(parents=True, exist_ok=True)

    student_id = student_data["student_id"]
    filename = f"{student_id}.pdf"
    filepath = storage_dir / filename

    # A6 landscape for ID card
    width, height = 148 * mm, 105 * mm
    c = canvas.Canvas(str(filepath), pagesize=(width, height))

    # Background
    c.setFillColor(colors.HexColor("#1e3a5f"))
    c.rect(0, 0, width, height, fill=1, stroke=0)

    # White content area
    c.setFillColor(colors.white)
    c.rect(4 * mm, 4 * mm, width - 8 * mm, height - 8 * mm, fill=1, stroke=0)

    # Header bar
    c.setFillColor(colors.HexColor("#1e3a5f"))
    c.rect(4 * mm, height - 22 * mm, width - 8 * mm, 18 * mm, fill=1, stroke=0)

    # Academy name in header
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(width / 2, height - 12 * mm, "BANO QABIL")
    c.setFont("Helvetica", 7)
    c.drawCentredString(width / 2, height - 17 * mm, "Student Identification Card")

    # Student photo area
    photo_x = 6 * mm
    photo_y = height - 55 * mm
    photo_w = 30 * mm
    photo_h = 30 * mm

    photo_path = student_data.get("photo_path")
    if photo_path:
        full_photo = Path(settings.STORAGE_PATH) / photo_path
        if full_photo.exists():
            c.drawImage(str(full_photo), photo_x, photo_y, photo_w, photo_h, preserveAspectRatio=True)
        else:
            _draw_placeholder_photo(c, photo_x, photo_y, photo_w, photo_h)
    else:
        _draw_placeholder_photo(c, photo_x, photo_y, photo_w, photo_h)

    # QR Code
    qr_path = student_data.get("qr_path")
    if qr_path:
        full_qr = Path(settings.STORAGE_PATH) / qr_path
        if full_qr.exists():
            qr_size = 28 * mm
            c.drawImage(str(full_qr), width - qr_size - 6 * mm, height - 58 * mm, qr_size, qr_size)

    # Student info
    info_x = 42 * mm
    c.setFillColor(colors.HexColor("#1e3a5f"))
    c.setFont("Helvetica-Bold", 10)
    c.drawString(info_x, height - 30 * mm, student_data.get("full_name", ""))

    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(colors.HexColor("#e74c3c"))
    c.drawString(info_x, height - 37 * mm, student_data.get("student_id", ""))

    c.setFont("Helvetica", 7.5)
    c.setFillColor(colors.HexColor("#333333"))

    fields = [
        ("Course:", student_data.get("course", "")),
        ("Batch:", student_data.get("batch", "")),
        ("Campus:", student_data.get("campus", "")),
        ("Phone:", student_data.get("phone", "")),
    ]
    y_pos = height - 44 * mm
    for label, value in fields:
        c.setFont("Helvetica-Bold", 7)
        c.drawString(info_x, y_pos, label)
        c.setFont("Helvetica", 7)
        c.drawString(info_x + 16 * mm, y_pos, str(value))
        y_pos -= 6 * mm

    # Footer bar
    c.setFillColor(colors.HexColor("#1e3a5f"))
    c.rect(4 * mm, 4 * mm, width - 8 * mm, 10 * mm, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica", 6.5)
    c.drawCentredString(width / 2, 7 * mm, "If found, please return to Bano Qabil Academy")

    c.save()
    return f"idcards/{filename}"


def _draw_placeholder_photo(c, x, y, w, h):
    c.setFillColor(colors.HexColor("#dde3ed"))
    c.rect(x, y, w, h, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#8899bb"))
    c.setFont("Helvetica", 6)
    c.drawCentredString(x + w / 2, y + h / 2, "Photo")
