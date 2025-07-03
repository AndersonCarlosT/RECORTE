import streamlit as st
from PIL import Image
import io

# Definir zonas predefinidas
zonas = {
    "Zona 1": {"left": 50, "top": 50, "right": 300, "bottom": 300},
    "Zona 2": {"left": 100, "top": 100, "right": 400, "bottom": 350},
    "Zona 3": {"left": 10, "top": 10, "right": 200, "bottom": 200},
}

st.title("Recorte de imagen por zonas predefinidas")

# Subir imagen
uploaded_file = st.file_uploader("Sube una imagen", type=["png", "jpg", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Imagen original", use_container_width=True)

    zona_seleccionada = st.selectbox("Selecciona la zona a recortar", list(zonas_predefinidas.keys()))
    coords = zonas_predefinidas[zona_seleccionada]

    # Recortar automáticamente al cambiar la zona
    cropped_image = image.crop((coords["left"], coords["top"], coords["right"], coords["bottom"]))
    st.image(cropped_image, caption=f"Recorte: {zona_seleccionada}", use_container_width=True)

    # Botón para descargar
    img_byte_arr = io.BytesIO()
    cropped_image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()

    st.download_button(
        label="Descargar imagen recortada",
        data=img_byte_arr,
        file_name=f"{zona_seleccionada.lower().replace(' ', '_')}.png",
        mime="image/png"
    )
