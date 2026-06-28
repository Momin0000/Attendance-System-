import qrcode
from qrcode.image.pure import PyPNGImage
import os
from pathlib import Path
from app.core.config import settings


def generate_qr_code(student_id: str) -> str:
    """
    Generate a QR code image for a student.
    QR contains only the student_id string (e.g., BQ-KHI-000001).
    Returns the relative path to the saved image.
    """
    storage_dir = Path(settings.STORAGE_PATH) / "qrcodes"
    storage_dir.mkdir(parents=True, exist_ok=True)

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(student_id)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    filename = f"{student_id}.png"
    filepath = storage_dir / filename
    img.save(str(filepath))

    return f"qrcodes/{filename}"
