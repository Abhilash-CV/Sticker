import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import barcode
from barcode.writer import ImageWriter
import io, zipfile

# ==========================
# LABEL SETTINGS
# ==========================
LABEL_WIDTH_CM = 6
LABEL_HEIGHT_CM = 3
DPI = 203  # 203 = thermal, 300 = laser

WIDTH_PX = int((LABEL_WIDTH_CM / 2.54) * DPI)
HEIGHT_PX = int((LABEL_HEIGHT_CM / 2.54) * DPI)

# ==========================
# UI
# ==========================
st.title("🖨️ Sticker Generator (Excel + Logo)")

logo_file = st.file_uploader("Upload Logo (PNG/JPG)", type=["png", "jpg", "jpeg"])
excel_file = st.file_uploader("Upload Excel File", type=["xlsx"])

if logo_file and excel_file and st.button("Generate Stickers"):

    df = pd.read_excel(excel_file)
    
    # Normalize column names
    df.columns = (
        df.columns
          .str.strip()       # remove spaces
          .str.lower()       # lowercase
          .str.replace(r"\s+", "", regex=True)  # remove hidden spaces
    )
    
    required_cols = {"code", "name", "district"}
    
    if not required_cols.issubset(set(df.columns)):
        st.error(f"Excel columns found: {list(df.columns)}")
        st.stop()

    logo = Image.open(logo_file).convert("RGBA")
    logo = logo.resize((60, 60))

    font_big = ImageFont.load_default()
    font_small = ImageFont.load_default()

    zip_buffer = io.BytesIO()
    zip_file = zipfile.ZipFile(zip_buffer, "w")

    for idx, row in df.iterrows():
        code = str(row["code"])
        name = str(row["name"])
        district = str(row["district"])

        img = Image.new("RGB", (WIDTH_PX, HEIGHT_PX), "white")
        draw = ImageDraw.Draw(img)

        # --------------------------
        # Logo (Top-Left)
        # --------------------------
        img.paste(logo, (10, 10), logo)

        # --------------------------
        # Center Text Helper
        # --------------------------
        def center_text(y, text, font):
            w = draw.textlength(text, font=font)
            x = (WIDTH_PX - w) // 2
            draw.text((x, y), text, fill="black", font=font)

        # --------------------------
        # Text
        # --------------------------
        center_text(10, code, font_big)
        center_text(35, name, font_big)
        center_text(60, district, font_small)

        # --------------------------
        # Barcode
        # --------------------------
        CODE128 = barcode.get_barcode_class("code128")
        bc = CODE128(code, writer=ImageWriter())

        bc_buffer = io.BytesIO()
        bc.write(bc_buffer, {"quiet_zone": 1})
        bc_buffer.seek(0)

        bc_img = Image.open(bc_buffer)
        bc_w = int(WIDTH_PX * 0.85)
        bc_h = int(HEIGHT_PX * 0.30)
        bc_img = bc_img.resize((bc_w, bc_h))

        bx = (WIDTH_PX - bc_w) // 2
        by = HEIGHT_PX - bc_h - 8
        img.paste(bc_img, (bx, by))

        # --------------------------
        # Save PNG
        # --------------------------
        img_buffer = io.BytesIO()
        img.save(img_buffer, format="PNG", dpi=(DPI, DPI))

        zip_file.writestr(f"{code}.png", img_buffer.getvalue())

    zip_file.close()
    zip_buffer.seek(0)

    st.success("Stickers generated successfully ✅")
    st.download_button(
        "⬇️ Download All Stickers (ZIP)",
        zip_buffer.getvalue(),
        "stickers.zip",
        mime="application/zip"
    )
