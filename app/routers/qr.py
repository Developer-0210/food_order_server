# app/routes/qr.py

import qrcode
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from io import BytesIO
from sqlalchemy.orm import Session
from app.models import Table
from app.db import get_db
from PIL import Image, ImageDraw, ImageFont

router = APIRouter(prefix="/qr", tags=["QR Code"])

@router.get("/{table_id}")
def generate_qr(
    table_id: int,
    db: Session = Depends(get_db),
):
    # Validate table
    table = db.query(Table).filter(Table.id == table_id).first()
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    if not table.admin:
        raise HTTPException(status_code=400, detail="Table not linked to a restaurant")

    cafe_name = table.admin.restaurant_name

    # Generate QR
    qr_url = f"https://www.jiffymenu.com/food?table_id={table.id}"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")

    try:
        # Load logo
        logo_path = "app/static/logo.png"
        logo = Image.open(logo_path).convert("RGBA")

        # Resize logo
        logo_height = 60
        ratio = logo.width / logo.height
        logo = logo.resize((int(logo_height * ratio), logo_height), Image.LANCZOS)

        # Create a new image with white background for QR + space below
        spacing = 20
        footer_height = 120  # space for text and logo
        final_img = Image.new("RGB", (qr_img.width, qr_img.height + footer_height), "white")

        # Paste QR on top
        final_img.paste(qr_img, (0, 0))

        draw = ImageDraw.Draw(final_img)

        # Load fonts
        try:
            font_large = ImageFont.truetype("arial.ttf", 24)
            font_small = ImageFont.truetype("arial.ttf", 16)
        except:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()

        # Draw "Welcome to {Cafe Name}"
        welcome_text = f"Welcome to {cafe_name}"
        text_w = draw.textlength(welcome_text, font=font_large)
        draw.text(((qr_img.width - text_w) // 2, qr_img.height + 10), welcome_text, font=font_large, fill="black")

        # Paste logo
        logo_x = (qr_img.width - logo.width) // 2
        logo_y = qr_img.height + 40
        final_img.paste(logo, (logo_x, logo_y), mask=logo)

        # Draw small footer
        powered_by = "Powered by JiffyMenu"
        small_text_w = draw.textlength(powered_by, font=font_small)
        draw.text(((qr_img.width - small_text_w) // 2, qr_img.height + 40 + logo.height + 5), powered_by, font=font_small, fill="gray")

    except FileNotFoundError:
        print("⚠️ Logo not found, generating QR without branding.")
        final_img = qr_img

    buffer = BytesIO()
    final_img.save(buffer, format="PNG")
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="image/png",
        headers={
            "Content-Disposition": f"attachment; filename=table_{table.table_number}_qr.png"
        },
    )
