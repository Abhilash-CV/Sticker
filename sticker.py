import streamlit as st
import pandas as pd
import io

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

from PIL import Image
import barcode
from barcode.writer import ImageWriter

# -------------------------------------------------
# LABEL & PAGE SETTINGS (EXACT SIZE)
# -------------------------------------------------
LABEL_WIDTH = 5 * cm     # 5 cm
LABEL_HEIGHT = 3 * cm    # 3 cm

PAGE_WIDTH, PAGE_HEIGHT = A4

COLS = int(PAGE_WIDTH // LABEL_WIDTH)
ROWS = int(PAGE_HEIGHT // LABEL_HEIGHT)

# -------------------------------------------------
# UI
# -------------------------------------------------
st.set_page_config(page_title="Sticker PDF Generator")
st.title("🖨️ Sticker PDF Generator (5 cm × 3 cm)")

logo_file = st.file_uploader("Upload Logo (PNG/JPG)", type=["png", "jpg", "jpeg"])
excel_file = st.file_uploader("Upload Excel File", type=["xlsx"])

# -------------------------------------------------
# PROCESS
# -------------------------------------------------
if logo_file and excel_file and st.button("Generate PDF"):

    # ---------------- Excel ----------------
    df = pd.read_excel(excel_file)

    # Normalize column names
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(r"\s+", "", regex=True)
    )

    if not {"code", "name", "district"}.issubset(df.columns):
        st.error(f"Excel columns found: {list(df.columns)}")
        st.stop()

    # ---------------- Logo (SAFE) ----------------
    logo_img = Image.open(logo_file).convert("RGBA")
    logo_reader = ImageReader(logo_img)

    # ---------------- PDF ----------------
    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=A4)

    col = 0
    row = 0

    for _, r in df.iterrows():

        x = col * LABEL_WIDTH
        y = PAGE_HEIGHT - ((row + 1) * LABEL_HEIGHT)

        # Optional border (cut guide)
        c.rect(x, y, LABEL_WIDTH, LABEL_HEIGHT)

        # -------- LOGO --------
        c.drawImage(
            logo_reader,
            x + 0.2 * cm,
            y + LABEL_HEIGHT - 1.4 * cm,
            width=1.2 * cm,
            height=1.2 * cm,
            mask="auto"
        )

        # -------- TEXT (Times Bold, 14 pt, Centered) --------
        c.setFont("Times-Bold", 14)

        c.drawCentredString(
            x + LABEL_WIDTH / 2,
            y + LABEL_HEIGHT - 0.8 * cm,
            str(r["code"])
        )

        c.drawCentredString(
            x + LABEL_WIDTH / 2,
            y + LABEL_HEIGHT - 1.4 * cm,
            str(r["name"])
        )

        c.drawCentredString(
            x + LABEL_WIDTH / 2,
            y + LABEL_HEIGHT - 2.0 * cm,
            str(r["district"])
        )

        # -------- BARCODE --------
        CODE128 = barcode.get_barcode_class("code128")
        bc = CODE128(str(r["code"]), writer=ImageWriter())

        bc_buffer = io.BytesIO()
        bc.write(bc_buffer, {"quiet_zone": 1, "module_height": 8})
        bc_buffer.seek(0)

        bc_img = Image.open(bc_buffer)
        bc_reader = ImageReader(bc_img)

        c.drawImage(
            bc_reader,
            x + 0.4 * cm,
            y + 0.2 * cm,
            width=LABEL_WIDTH - 0.8 * cm,
            height=0.8 * cm,
            mask="auto"
        )

        # -------- GRID MANAGEMENT --------
        col += 1
        if col >= COLS:
            col = 0
            row += 1

        if row >= ROWS:
            c.showPage()
            row = 0

    c.save()
    pdf_buffer.seek(0)

    # ---------------- DOWNLOAD ----------------
    st.success("PDF generated successfully ✅")

    st.download_button(
        label="⬇️ Download Sticker PDF",
        data=pdf_buffer,
        file_name="stickers_5x3cm.pdf",
        mime="application/pdf"
    )
