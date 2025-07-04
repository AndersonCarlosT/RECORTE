import streamlit as st
from PIL import Image, ImageDraw, ImageEnhance
import io
import zipfile

# Zonas predefinidas
zonas_predefinidas = {
    "1 Fila": {"left": 425, "top": 200, "right": 1882, "bottom": 485},
    "2 Filas": {"left": 425, "top": 200, "right": 1882, "bottom": 510},
    "3 Filas": {"left": 425, "top": 200, "right": 1882, "bottom": 533},
    "4 Filas": {"left": 425, "top": 200, "right": 1882, "bottom": 555},
    "5 Filas": {"left": 425, "top": 200, "right": 1882, "bottom": 578},
}

st.title("Recorte masivo de imágenes por zona predefinida")

# Subir varias imágenes
uploaded_files = st.file_uploader("Sube una o más imágenes", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

if uploaded_files:
    zona_seleccionada = st.selectbox("Selecciona una zona de recorte", list(zonas_predefinidas.keys()))
    coords = zonas_predefinidas[zona_seleccionada]

    # Mostrar solo una imagen de muestra (la primera)
    muestra = Image.open(uploaded_files[0]).convert("RGBA")
    enhancer = ImageEnhance.Brightness(muestra)
    darkened = enhancer.enhance(0.3)
    mask = Image.new("L", muestra.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rectangle((coords["left"], coords["top"], coords["right"], coords["bottom"]), fill=255)
    resaltada = Image.composite(muestra, darkened, mask)

    st.markdown("#### 🖼️ Imagen referencial (vista previa del recorte seleccionado)")
    st.image(resaltada, caption=f"Vista previa en: {uploaded_files[0].name}", use_container_width=True)

    # Recortar todas las imágenes
    st.subheader("Descargas individuales")

    recortes_zip = io.BytesIO()
    with zipfile.ZipFile(recortes_zip, mode="w") as zipf:
        for idx, uploaded_file in enumerate(uploaded_files):
            img = Image.open(uploaded_file).convert("RGBA")
            recorte = img.crop((coords["left"], coords["top"], coords["right"], coords["bottom"]))

            # Guardar recorte para descarga individual
            img_bytes = io.BytesIO()
            recorte.convert("RGB").save(img_bytes, format='PNG')
            img_bytes_value = img_bytes.getvalue()

            # Mostrar botón de descarga individual
            st.download_button(
                label=f"Descargar recorte: {uploaded_file.name}",
                data=img_bytes_value,
                file_name=f"recorte_{idx+1}_{zona_seleccionada.lower().replace(' ', '_')}.png",
                mime="image/png"
            )

            # Agregar al ZIP
            zipf.writestr(f"recorte_{idx+1}_{zona_seleccionada.lower().replace(' ', '_')}.png", img_bytes_value)

    st.subheader("Descarga masiva (ZIP)")
    recortes_zip.seek(0)
    st.download_button(
        label="Descargar todos los recortes (.zip)",
        data=recortes_zip,
        file_name="recortes.zip",
        mime="application/zip"
    )

