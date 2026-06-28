import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT


CARD_WIDTH = 85.6 * mm   # ISO CR80 card width
CARD_HEIGHT = 54 * mm    # ISO CR80 card height


def generate_student_id_card(student, output_dir: str) -> str:
    """
    Generate a student ID card PDF (ISO CR80 size) and return the file path.
    """
    os.makedirs(output_dir, exist_ok=True)
    filename = f"id_card_{student.student_id}.pdf"
    filepath = os.path.join(output_dir, filename)

    doc = SimpleDocTemplate(
        filepath,
        pagesize=(CARD_WIDTH, CARD_HEIGHT),
        leftMargin=4 * mm,
        rightMargin=4 * mm,
        topMargin=4 * mm,
        bottomMargin=4 * mm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "title",
        parent=styles["Normal"],
        fontSize=7,
        fontName="Helvetica-Bold",
        textColor=colors.white,
        alignment=TA_CENTER,
    )
    label_style = ParagraphStyle(
        "label",
        parent=styles["Normal"],
        fontSize=5,
        fontName="Helvetica",
        textColor=colors.grey,
        alignment=TA_LEFT,
    )
    value_style = ParagraphStyle(
        "value",
        parent=styles["Normal"],
        fontSize=6,
        fontName="Helvetica-Bold",
        textColor=colors.black,
        alignment=TA_LEFT,
    )
    id_style = ParagraphStyle(
        "id",
        parent=styles["Normal"],
        fontSize=6,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#003366"),
        alignment=TA_CENTER,
    )

    elements = []

    # Header band
    header_data = [[Paragraph("BANO QABIL PAKISTAN", title_style)]]
    header_table = Table(header_data, colWidths=[CARD_WIDTH - 8 * mm], rowHeights=[8 * mm])
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#003366")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 2 * mm))

    # Body: photo on left, details on right
    photo_cell_content = []
    if student.photo_path and os.path.exists(student.photo_path):
        photo = RLImage(student.photo_path, width=15 * mm, height=18 * mm)
        photo_cell_content.append(photo)
    else:
        photo_cell_content.append(Paragraph("No Photo", label_style))

    # QR code
    qr_cell_content = []
    if student.qr_code_path and os.path.exists(student.qr_code_path):
        qr = RLImage(student.qr_code_path, width=14 * mm, height=14 * mm)
        qr_cell_content.append(qr)

    full_name = f"{student.first_name} {student.last_name}"
    detail_content = [
        Paragraph("STUDENT ID CARD", ParagraphStyle("sub", parent=styles["Normal"], fontSize=5.5, fontName="Helvetica-Bold", textColor=colors.HexColor("#003366"), alignment=TA_LEFT)),
        Spacer(1, 1 * mm),
        Paragraph("Name:", label_style),
        Paragraph(full_name, value_style),
        Spacer(1, 0.5 * mm),
        Paragraph("Course:", label_style),
        Paragraph(getattr(student, "_course_name", "N/A"), value_style),
        Spacer(1, 0.5 * mm),
        Paragraph("Campus:", label_style),
        Paragraph(getattr(student, "_campus_name", "N/A"), value_style),
    ]

    body_data = [[photo_cell_content, detail_content, qr_cell_content]]
    body_table = Table(
        body_data,
        colWidths=[17 * mm, 42 * mm, 16 * mm],
        rowHeights=[28 * mm]
    )
    body_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (0, 0), (0, -1), "CENTER"),
        ("ALIGN", (2, 0), (2, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
    ]))
    elements.append(body_table)
    elements.append(Spacer(1, 1 * mm))

    # Footer with student ID
    footer_data = [[Paragraph(f"ID: {student.student_id}", id_style)]]
    footer_table = Table(footer_data, colWidths=[CARD_WIDTH - 8 * mm], rowHeights=[6 * mm])
    footer_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#E8F0FE")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#003366")),
    ]))
    elements.append(footer_table)

    doc.build(elements)
    return filepath
