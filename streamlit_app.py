import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="DocuMind AI Pro", page_icon="📚", layout="centered")

# --- CONFIGURACIÓN OCULTA ---
MODELO_USADO = "models/gemini-1.5-flash"

# --- 1. AUTENTICACIÓN INVISIBLE ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except FileNotFoundError:
    st.error("⚠️ Error: No se encontró la API Key en los secretos.")
    st.stop()

# --- INTERFAZ ---
st.title("📚 DocuMind: Análisis Multi-Documento")
st.markdown(f"""
    <div style="padding: 10px; background-color: #f0f2f6; border-radius: 8px; font-size: 0.8em; color: #555;">
        POTENCIADO POR: <strong>Google {MODELO_USADO.replace('models/', '').upper()}</strong><br>
        Sube varios archivos y haz preguntas cruzadas (Ej: "Compara el documento 1 con el 2").
    </div>
    """, unsafe_allow_html=True)

st.divider()

# --- 2. CARGA DE PDFS (Ahora Múltiples) ---
# accept_multiple_files=True es la clave aquí
pdf_files = st.file_uploader("Sube tus documentos (PDF)", type=['pdf'], accept_multiple_files=True)

if pdf_files:
    # Botón manual para procesar (mejor cuando son varios archivos)
    if st.button(f"🧠 Procesar {len(pdf_files)} Documentos"):
        with st.spinner("Fusionando conocimientos..."):
            try:
                full_text = ""
                # Bucle: Leemos cada PDF uno por uno
                for pdf in pdf_files:
                    reader = PdfReader(pdf)
                    # Añadimos un encabezado para que la IA sepa dónde empieza cada uno
                    full_text += f"\n\n--- INICIO DEL DOCUMENTO: {pdf.name} ---\n"
                    for page in reader.pages:
                        full_text += page.extract_text() or ""
                    full_text += f"\n--- FIN DEL DOCUMENTO: {pdf.name} ---\n"
                
                # Guardamos TODO el texto junto en la memoria
                st.session_state['text'] = full_text
                st.success(f"✅ Éxito: Se leyeron {len(pdf_files)} archivos correctamente.")
                
            except Exception as e:
                st.error(f"Error leyendo los PDFs: {e}")

# --- 3. CHAT ---
if 'text' in st.session_state:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Pregunta sobre los documentos..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                model = genai.GenerativeModel(MODELO_USADO)
                # Prompt actualizado para manejar múltiples fuentes
                full_prompt = f"""
                Actúa como un analista experto. Tienes acceso a uno o varios documentos.
                Usa el siguiente contexto para responder.
                
                IMPORTANTE: Si la información viene de un documento específico, menciona su nombre (ej: "Según el reporte A...").
                
                CONTEXTO COMBINADO:
                {st.session_state['text']}
                
                PREGUNTA:
                {prompt}
                """
                response = model.generate_content(full_prompt)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                
            except Exception as e:
                st.error(f"Error de conexión: {e}")
