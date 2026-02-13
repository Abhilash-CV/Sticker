import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import barcode
from barcode.writer import ImageWriter
import io

# ---------------------------
# Page Setup
# ---------------------------
st.set_page_config(page_title="Sticker Generator", layout="centered")
st.title("🖨️ Sticker Generator")

# ---------------------------
# User Inputs
# ---------------------------
logo_file = st.file_uploader("Upload Logo (PNG/JPG)", type=["png", "jpg", "jpeg"])
computer_no = st.text_input("Computer Number", "COM-001")
barcode_value = st.text_input("Barcode Value", "COM001")

generate = st.button("Generate Sticker")

# ---------------------------
# Generate Sticker
# ---------------------------
if generate:
    # Sticker size (in pixels)
    WIDTH, HEIGHT = 400, 200
    sticker = Image.new("RGB", (WIDTH, HEIGHT), "white")
    draw = ImageDraw.Draw(sticker)

    # ---------------------------
    # Load Logo
    # ---------------------------
    if logo_file:
        logo = Image.open(logo_file).convert("RGBA")
        logo = logo.resize((80, 80))
        sticker.paste(logo, (10, 10), logo)

    # ---------------------------
    # Text
    # ---------------------------
    try:
        font = ImageFont.truetype("arial.ttf", 22)
    except:
        font = ImageFont.load_default()

    draw.text((110, 20), f"Computer No:", fill="black", font=font)
    draw.text((110, 50), computer_no, fill="black", font=font)

    # ---------------------------
    # Barcode Generation
    # ---------------------------
    CODE128 = barcode.get_barcode_class("code128")
    barcode_img = CODE128(barcode_value, writer=ImageWriter())

    barcode_buffer = io.BytesIO()
    barcode_img.write(barcode_buffer)
    barcode_buffer.seek(0)

    barcode_pil = Image.open(barcode_buffer)
    barcode_pil = barcode_pil.resize((300, 60))

    sticker.paste(barcode_pil, (50, 120))

    # ---------------------------
    # Display Sticker
    # ---------------------------
    st.image(sticker, caption="Generated Sticker", use_container_width=False)

    # ---------------------------
    # Download Button
    # ---------------------------
    output = io.BytesIO()
    sticker.save(output, format="PNG")
    st.download_button(
        label="⬇️ Download Sticker",
        data=output.getvalue(),
        file_name=f"{computer_no}_sticker.png",
        mime="image/png"
    )
