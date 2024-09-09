import streamlit as st
from PIL import Image
import numpy as np
import cv2
from fpdf import FPDF

# Función para calcular proporciones
def calculate_dimensions(known_height, known_pixel_height, total_pixel_height):
    return (total_pixel_height / known_pixel_height) * known_height

# Función para dibujar cotas de medición en la imagen
def draw_measurements(image, total_height, total_width):
    img_copy = image.copy()
    
    # Dibujar línea vertical para la altura
    start_point = (int(img_copy.shape[1] * 0.1), int(img_copy.shape[0] * 0.1))
    end_point = (int(img_copy.shape[1] * 0.1), int(img_copy.shape[0] * 0.9))
    cv2.line(img_copy, start_point, end_point, (0, 255, 0), 2)
    
    # Agregar texto de la altura
    text = f'Altura: {total_height:.2f} m'
    cv2.putText(img_copy, text, (int(img_copy.shape[1] * 0.1 + 10), int(img_copy.shape[0] * 0.5)), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # Dibujar línea horizontal para el ancho
    start_point = (int(img_copy.shape[1] * 0.1), int(img_copy.shape[0] * 0.9))
    end_point = (int(img_copy.shape[1] * 0.9), int(img_copy.shape[0] * 0.9))
    cv2.line(img_copy, start_point, end_point, (255, 0, 0), 2)
    
    # Agregar texto del ancho
    text = f'Ancho: {total_width:.2f} m'
    cv2.putText(img_copy, text, (int(img_copy.shape[1] * 0.5), int(img_copy.shape[0] * 0.95)), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
    
    return img_copy

# Función para generar el PDF
def export_to_pdf(total_height, total_width):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(200, 10, txt="Estimaciones de Dimensiones del Edificio", ln=True, align='C')
    pdf.ln(10)
    
    # Detalles de las medidas
    pdf.set_font('Arial', '', 12)
    pdf.cell(200, 10, txt=f"Altura total aproximada: {total_height:.2f} metros", ln=True)
    pdf.cell(200, 10, txt=f"Ancho total aproximado: {total_width:.2f} metros", ln=True)
    
    # Guardar el PDF en un archivo temporal
    return pdf.output(dest='S').encode('latin1')

# Configurar la app en Streamlit
st.title("🏢 Estimador de Medidas de Edificios con Cotas de Medición")

# Subir la imagen
uploaded_file = st.file_uploader("Sube una imagen del edificio", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    img_cv = np.array(image.convert('RGB'))
    img_cv = cv2.cvtColor(img_cv, cv2.COLOR_RGB2BGR)
    
    st.image(image, caption="Imagen cargada", use_column_width=True)
    
    # Pedir entrada del usuario para una medida conocida (ej. altura de ventana)
    known_height = st.number_input("Introduce la altura conocida (ej. altura de una ventana en metros):", min_value=0.1, step=0.1)
    
    if known_height:
        st.write("Selecciona el área correspondiente a la altura conocida (ej. la ventana)")
        known_pixel_height = st.slider("Selecciona la altura en píxeles (por ejemplo, selecciona la altura de la ventana):", min_value=1, max_value=img_cv.shape[0], value=100)

        if st.button("Calcular Dimensiones"):
            total_pixel_height = st.slider("Selecciona la altura total del edificio en píxeles:", min_value=1, max_value=img_cv.shape[0], value=img_cv.shape[0]//2)
            total_pixel_width = st.slider("Selecciona el ancho total del edificio en píxeles:", min_value=1, max_value=img_cv.shape[1], value=img_cv.shape[1]//2)
            
            # Calcular dimensiones
            total_height = calculate_dimensions(known_height, known_pixel_height, total_pixel_height)
            total_width = calculate_dimensions(known_height, known_pixel_height, total_pixel_width)
            
            st.write(f"Altura total aproximada del edificio: {total_height:.2f} metros")
            st.write(f"Ancho total aproximado del edificio: {total_width:.2f} metros")
            
            # Dibujar cotas en la imagen
            img_with_measurements = draw_measurements(img_cv, total_height, total_width)
            
            # Convertir imagen a formato PIL para mostrar en Streamlit
            img_with_measurements_pil = Image.fromarray(cv2.cvtColor(img_with_measurements, cv2.COLOR_BGR2RGB))
            st.image(img_with_measurements_pil, caption="Imagen con cotas de medición", use_column_width=True)

            # Guardar imagen como archivo
            img_path = "imagen_con_cotas.jpg"
            cv2.imwrite(img_path, img_with_measurements)
            
            # Descargar la imagen con cotas
            with open(img_path, "rb") as file:
                btn = st.download_button(
                    label="Descargar imagen con cotas",
                    data=file,
                    file_name="imagen_con_cotas.jpg",
                    mime="image/jpeg"
                )

            # Botón para exportar el PDF
            pdf_data = export_to_pdf(total_height, total_width)
            st.download_button(
                label="Descargar resultados en PDF",
                data=pdf_data,
                file_name="estimaciones_edificio.pdf",
                mime="application/octet-stream"
            )
