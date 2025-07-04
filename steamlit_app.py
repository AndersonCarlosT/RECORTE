import streamlit as st
from PIL import Image, ImageDraw, ImageEnhance
import io
import zipfile
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
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

    # Dimensiones de la página en puntos
    page_width, page_height = A4
    y_position = page_height - inch  # 1 pulgada de margen arriba

    for recorte in recortes_para_pdf:
        img_width, img_height = recorte.size

        # Escalamos si el ancho supera el máximo permitido (por ejemplo 6.5 pulgadas)
        max_width_points = 6.5 * inch  # ≈ 468 pts
        scale_factor = min(1.0, max_width_points / img_width)

        final_width = img_width * scale_factor
        final_height = img_height * scale_factor

        # Si no hay suficiente espacio en la página, pasar a la siguiente
        if y_position - final_height < inch:
            c.showPage()
            y_position = page_height - inch

        # Guardar imagen temporal
        img_bytes = io.BytesIO()
        recorte.save(img_bytes, format='PNG')
        img_bytes.seek(0)

        # Dibujar imagen con escala calculada
        c.drawImage(ImageReader(img_bytes), inch, y_position - final_height, width=final_width, height=final_height)
        y_position -= final_height + 20  # espacio entre imágenes

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

