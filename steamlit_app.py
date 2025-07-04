import streamlit as st
from PIL import Image, ImageDraw, ImageEnhance
import io
import zipfile
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# Zonas predefinidas
zonas_predefinidas = {
    "1 Fila": {"left": 425, "top": 200, "right": 1882, "bottom": 485},
    "2 Filas": {"left": 425, "top": 200, "right": 1882, "bottom": 510},
    "3 Filas": {"left": 425, "top": 200, "right": 1882, "bottom": 533},
    "4 Filas": {"left": 425, "top": 200, "right": 1882, "bottom": 555},
    "5 Filas": {"left": 425, "top": 200, "right": 1882, "bottom": 578},
}

st.title("Recorte masivo de imágenes por zona predefinida")

uploaded_files = st.file_uploader("Sube una o más imágenes", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

if uploaded_files:
    zona_seleccionada = st.selectbox("Selecciona una zona de recorte", list(zonas_predefinidas.keys()))
    coords = zonas_predefinidas[zona_seleccionada]

    # Mostrar imagen de muestra
    muestra = Image.open(uploaded_files[0]).convert("RGBA")
    enhancer = ImageEnhance.Brightness(muestra)
    darkened = enhancer.enhance(0.3)
    mask = Image.new("L", muestra.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rectangle((coords["left"], coords["top"], coords["right"], coords["bottom"]), fill=255)
    resaltada = Image.composite(muestra, darkened, mask)

    st.markdown("#### 🖼️ Imagen referencial (vista previa del recorte seleccionado)")
    st.image(resaltada, caption=f"Vista previa en: {uploaded_files[0].name}", use_container_width=True)

    # ZIP para los recortes
    recortes_zip = io.BytesIO()
    with zipfile.ZipFile(recortes_zip, mode="w") as zipf:
        # Preparar lista de recortes para el PDF también
        recortes_para_pdf = []

        for idx, uploaded_file in enumerate(uploaded_files):
            img = Image.open(uploaded_file).convert("RGBA")
            recorte = img.crop((coords["left"], coords["top"], coords["right"], coords["bottom"]))
            recorte = recorte.convert("RGB")  # Para guardar en PDF

            # Guardar recorte como PNG en ZIP
            img_bytes = io.BytesIO()
            recorte.save(img_bytes, format='PNG')
            img_bytes_value = img_bytes.getvalue()

            nombre_base = uploaded_file.name.rsplit(".", 1)[0]
            zipf.writestr(f"{nombre_base}_recorte.png", img_bytes_value)

            # Guardar en lista para PDF
            recortes_para_pdf.append(recorte)

    # Descargar ZIP
    st.subheader("📦 Descargar todos los recortes")
    recortes_zip.seek(0)
    st.download_button(
        label="Descargar .zip",
        data=recortes_zip,
        file_name="recortes.zip",
        mime="application/zip"
    )

    # Crear PDF con imágenes una debajo de otra
    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=A4)
    max_width = 500  # Máximo ancho para las imágenes en el PDF
    margin_top = 800  # posición vertical inicial (A4 alto = 842)

    for recorte in recortes_para_pdf:
        width, height = recorte.size

        # Escalar si es necesario
        if width > max_width:
            ratio = max_width / width
            width = max_width
            height = int(height * ratio)
            recorte = recorte.resize((width, height))

        # Guardar imagen temporal en bytes
        img_bytes = io.BytesIO()
        recorte.save(img_bytes, format='PNG')
        img_bytes.seek(0)

        if margin_top - height < 40:
            c.showPage()
            margin_top = 800

        c.drawImage(ImageReader(img_bytes), 50, margin_top - height, width=width, height=height)
        margin_top -= (height + 20)

    c.save()
    pdf_buffer.seek(0)

    # Botón para descargar el PDF
    st.subheader("📄 Descargar PDF con los recortes")
    st.download_button(
        label="Descargar PDF",
        data=pdf_buffer,
        file_name="recortes.pdf",
        mime="application/pdf"
    )

