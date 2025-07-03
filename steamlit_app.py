import streamlit as st
from PIL import Image, ImageDraw, ImageEnhance
import io

# Zonas predefinidas
zonas_predefinidas = {
    "1 Fila": {"left": 425, "top": 200, "right": 1882, "bottom": 485},
    "2 Filas": {"left": 425, "top": 200, "right": 1882, "bottom": 510},
    "3 Filas": {"left": 425, "top": 200, "right": 1882, "bottom": 533},
    "4 Filas": {"left": 425, "top": 200, "right": 1882, "bottom": 555},
    "5 Filas": {"left": 425, "top": 200, "right": 1882, "bottom": 578},
}

st.title("Recorte por zonas en múltiples imágenes")

# Subir varias imágenes
uploaded_files = st.file_uploader("Sube una o más imágenes", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

if uploaded_files:
    zona_seleccionada = st.selectbox("Selecciona una zona", list(zonas_predefinidas.keys()))
    coords = zonas_predefinidas[zona_seleccionada]

    for idx, uploaded_file in enumerate(uploaded_files):
        st.markdown(f"---\n### Imagen {idx + 1}: {uploaded_file.name}")
        image = Image.open(uploaded_file).convert("RGBA")

        # Crear imagen con zona resaltada
        enhancer = ImageEnhance.Brightness(image)
        darkened = enhancer.enhance(0.3)

        mask = Image.new("L", image.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rectangle((coords["left"], coords["top"], coords["right"], coords["bottom"]), fill=255)

        result = Image.composite(image, darkened, mask)
        st.image(result, caption=f"Zona resaltada: {zona_seleccionada}", use_container_width=True)

        # Recortar zona
        cropped_image = image.crop((coords["left"], coords["top"], coords["right"], coords["bottom"]))

        img_byte_arr = io.BytesIO()
        cropped_image.convert("RGB").save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()

        st.download_button(
            label=f"Descargar recorte ({uploaded_file.name})",
            data=img_byte_arr,
            file_name=f"recorte_{idx+1}_{zona_seleccionada.lower().replace(' ', '_')}.png",
            mime="image/png"
        )
