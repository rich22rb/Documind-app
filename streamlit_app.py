import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="DocuMind AI", page_icon="⚡", layout="centered")

# --- CONFIGURACIÓN OCULTA (HARDCODED) ---
MODELO_USADO = "models/gemini-1.5-flash"  # El modelo rápido y gratis

# --- 1. AUTENTICACIÓN INVISIBLE ---
try:
    # Busca la llave en los secretos de Streamlit
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except FileNotFoundError:
    st.error("⚠️ Error de Configuración: No se encontró la API Key en los secretos.")
    st.stop()

# --- INTERFAZ DE USUARIO ---
st.title("⚡ DocuMind: Análisis Instantáneo")
st.markdown(f"""
    <style>
    .info-box {{ padding: 10px; background-color: #f0f2f6; border-radius: 8px; font-size: 0.8em; color: #555; }}
    </style>
    <div class="info-box">
        POTENCIADO POR: <strong>Google {MODELO_USADO.replace('models/', '').upper()}</strong><br>
        Esta tecnología analiza tu documento en segundos sin almacenar datos personales.
    </div>
    """, unsafe_allow_html=True)

st.divider()

# --- 2. CARGA DE PDF ---
pdf_file = st.file_uploader("Sube tu documento (PDF)", type=['pdf'])

if pdf_file:
    # Procesamiento automático al subir
    with st.spinner("⏳ Leyendo documento a velocidad luz..."):
        try:
            reader = PdfReader(pdf_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            
            # Guardamos el texto en memoria
            st.session_state['text'] = text
            st.success(f"✅ Documento procesado ({len(text)} caracteres leídos).")
            
        except Exception as e:
            st.error(f"Error leyendo el PDF: {e}")

# --- 3. CHAT ---
if 'text' in st.session_state:
    # Historial de chat
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Mostrar mensajes previos
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Input del usuario
    if prompt := st.chat_input("Pregunta algo sobre el documento..."):
        # Guardar y mostrar pregunta
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generar respuesta
        with st.chat_message("assistant"):
            try:
                model = genai.GenerativeModel(MODELO_USADO)
                # Prompt de ingeniería para que se comporte bien
                full_prompt = f"""
                Actúa como un analista experto. Usa el siguiente contexto para responder la pregunta.
                Si la respuesta no está en el texto, dilo. Sé conciso y profesional.
                
                CONTEXTO:
                {st.session_state['text']}
                
                PREGUNTA:
                {prompt}
                """
                response = model.generate_content(full_prompt)
                st.markdown(response.text)
                
                # Guardar respuesta
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                
            except Exception as e:
                st.error(f"Error de conexión: {e}")
