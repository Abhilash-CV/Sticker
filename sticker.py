import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import barcode
from barcode.writer import ImageWriter
import io

# ---------------------------
# SETTINGS
# ---------------------------
LABEL_WIDTH_CM = 6
LABEL_HEIGHT_CM = 3
DPI = 203   # Use 300 for laser printers

WIDTH_PX = int((LABEL_WIDTH_CM / 2.54) * DPI)
HEIGHT_PX = int((LABEL_HEIGHT_CM / 2.54) * DPI)

# ---------------------------
# UI
# ---------------------------
st.title("🖨️ Sticker Generator (Exact Size)")

code = st.text_input("Center Code", "PC-001")
name = st.text_input("Center Name", "Government HSS")
district = st.text_input("District", "Ernakulam")

if st.button("Generate Sticker"):

    # Canvas
    img = Image.new("RGB", (WIDTH_PX, HEIGHT_PX), "white")
    draw = ImageDraw.Draw(img)

    # Fonts (Linux-safe)
    font_big = ImageFont.load_default()
    font_small = ImageFont.load_default()

    # ---------------------------
    # Helper: Center Text
    # ---------------------------
    def center_text(y, text, font):
        w = draw.textlength(text, font=font)
        x = (WIDTH_PX - w) // 2
        draw.text((x, y), text, fill="black", font=font)

    # ---------------------------
    # Text Layout (TOP → DOWN)
    # ---------------------------
    center_text(10, code, font_big)
    center_text(35, name, font_big)
    center_text(60, district, font_small)

    # ---------------------------
    # Barcode
    # ---------------------------
    CODE128 = barcode.get_barcode_class("code128")
    bc = CODE128(code, writer=ImageWriter())

    buffer = io.BytesIO()
    bc.write(buffer, {"quiet_zone": 1})
    buffer.seek(0)

    barcode_img = Image.open(buffer)
    barcode_width = int(WIDTH_PX * 0.85)
    barcode_height = int(HEIGHT_PX * 0.30)
    barcode_img = barcode_img.resize((barcode_width, barcode_height))

    bx = (WIDTH_PX - barcode_width) // 2
    by = HEIGHT_PX - barcode_height - 10
    img.paste(barcode_img, (bx, by))

    # ---------------------------
    # Preview
    # ---------------------------
    st.image(img, caption=f"{LABEL_WIDTH_CM}cm × {LABEL_HEIGHT_CM}cm @ {DPI} DPI")

    # ---------------------------
    # Download
    # ---------------------------
    out = io.BytesIO()
    img.save(out, format="PNG", dpi=(DPI, DPI))

    st.download_button(
        "⬇️ Download Sticker",
        out.getvalue(),
        file_name=f"{code}_label.png",
        mime="image/png"
    )
