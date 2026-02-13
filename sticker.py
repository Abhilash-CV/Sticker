import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import barcode
from barcode.writer import ImageWriter
import io
from PIL import Image

# ---------------------------
# REGISTER FONT
# ---------------------------
pdfmetrics.registerFont(
    TTFont("Times-Bold", "Times New Roman Bold.ttf")
)

# ---------------------------
# LABEL SIZE (EXACT)
# ---------------------------
LABEL_W = 5 * cm
LABEL_H = 3 * cm

PAGE_W, PAGE_H = A4

COLS = int(PAGE_W // LABEL_W)
ROWS = int(PAGE_H // LABEL_H)

# ---------------------------
# UI
# ---------------------------
st.title("🖨️ Sticker PDF Generator (5cm × 3cm)")

logo_file = st.file_uploader("Upload Logo (PNG/JPG)", type=["png", "jpg", "jpeg"])
excel_file = st.file_uploader("Upload Excel", type=["xlsx"])

if logo_file and excel_file and st.button("Generate PDF"):

    df = pd.read_excel(excel_file)

    # Normalize columns
    df.columns = (
        df.columns.str.strip().str.lower().str.replace(r"\s+", "", regex=True)
    )

    required = {"code", "name", "district"}
    if not required.issubset(df.columns):
        st.error(f"Excel columns detected: {list(df.columns)}")
        st.stop()

    logo_img = Image.open(logo_file)
    logo_buffer = io.BytesIO()
    logo_img.save(logo_buffer, format="PNG")
    logo_buffer.seek(0)

    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=A4)

    x_start = 0
    y_start = PAGE_H - LABEL_H
    col = row = 0

    for _, r in df.iterrows():
        x = x_start + col * LABEL_W
        y = y_start - row * LABEL_H

        # Border (optional – comment if not needed)
        c.rect(x, y, LABEL_W, LABEL_H)

        # Logo
        c.drawImage(logo_buffer, x + 0.2*cm, y + LABEL_H - 1.4*cm,
                    width=1.2*cm, height=1.2*cm, mask='auto')

        # Center Text
        c.setFont("Times-Bold", 14)

        c.drawCentredString(x + LABEL_W/2, y + LABEL_H - 0.8*cm, str(r["code"]))
        c.drawCentredString(x + LABEL_W/2, y + LABEL_H - 1.4*cm, str(r["name"]))
        c.drawCentredString(x + LABEL_W/2, y + LABEL_H - 2.0*cm, str(r["district"]))

        # Barcode
        code128 = barcode.get_barcode_class("code128")
        bc = code128(str(r["code"]), writer=ImageWriter())

        bc_buffer = io.BytesIO()
        bc.write(bc_buffer, {"module_height": 8, "quiet_zone": 1})
        bc_buffer.seek(0)

        c.drawImage(
            bc_buffer,
            x + 0.4*cm,
            y + 0.2*cm,
            width=LABEL_W - 0.8*cm,
            height=0.8*cm,
            mask='auto'
        )

        col += 1
        if col >= COLS:
            col = 0
            row += 1

        if row >= ROWS:
            c.showPage()
            row = 0

    c.save()
    pdf_buffer.seek(0)

    st.success("PDF generated successfully ✅")

    st.download_button(
        "⬇️ Download Sticker PDF",
        pdf_buffer,
        file_name="stickers_5x3cm.pdf",
        mime="application/pdf"
    )
