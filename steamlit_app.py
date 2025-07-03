import streamlit as st
from PIL import Image, ImageDraw, ImageEnhance
import io

# Diccionario de zonas predefinidas
zonas_predefinidas = {
    "Zona 1": {"left": 425, "top": 200, "right": 1890, "bottom": 600},
    "Zona 2": {"left": 100, "top": 100, "right": 400, "bottom": 350},
    "Zona 3": {"left": 10, "top": 10, "right": 200, "bottom": 200},
}

st.title("Visualizador de Zonas Recortadas")

# Subir imagen
uploaded_file = st.file_uploader("Sube una imagen", type=["png", "jpg", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGBA")  # Aseguramos canal alfa
    zona_seleccionada = st.selectbox("Selecciona una zona", list(zonas_predefinidas.keys()))
    coords = zonas_predefinidas[zona_seleccionada]

    # Crear una copia oscurecida de la imagen
    enhancer = ImageEnhance.Brightness(image)
    darkened = enhancer.enhance(0.3)

    # Crear una máscara en blanco y negro donde la zona recortada es blanca (visible)
    mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rectangle((coords["left"], coords["top"], coords["right"], coords["bottom"]), fill=255)

    # Combinar imagen original y fondo oscuro usando la máscara
    result = Image.composite(image, darkened, mask)

    st.image(result, caption=f"Zona resaltada: {zona_seleccionada}", use_container_width=True)

    # También recortar solo esa zona para descarga
    cropped_image = image.crop((coords["left"], coords["top"], coords["right"], coords["bottom"]))

    img_byte_arr = io.BytesIO()
    cropped_image.convert("RGB").save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()

    st.download_button(
        label="Descargar zona recortada",
        data=img_byte_arr,
        file_name=f"{zona_seleccionada.lower().replace(' ', '_')}.png",
        mime="image/png"
    )

