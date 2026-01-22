import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader

st.set_page_config(page_title="DocuMind AI", page_icon="🛡️", layout="centered")

# --- AUTENTICACIÓN ---
try:
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
    else:
        st.error("⚠️ Faltan los secretos. Configura GOOGLE_API_KEY en Streamlit.")
        st.stop()
except Exception as e:
    st.error(f"Error de configuración: {e}")
    st.stop()

# --- FUNCIÓN: BUSCADOR DE MODELOS ---
def get_best_model():
    """Prueba modelos en orden de prioridad hasta que uno responda"""
    # Lista de prioridades: Del más nuevo al más viejo (pero seguro)
    candidatos = [
        "gemini-1.5-flash",          # El ideal
        "gemini-1.5-flash-latest",   # Variación del ideal
        "gemini-pro"                 # El viejo confiable (si todo falla)
    ]
    
    # 1. Primero preguntamos a la cuenta qué tiene disponible
    try:
        mis_modelos = [m.name.replace("models/", "") for m in genai.list_models()]
    except:
        mis_modelos = []

    # 2. Cruzamos la lista
    for modelo in candidatos:
        # Opción A: Está en la lista oficial de tu cuenta
        if modelo in mis_modelos:
            return modelo
        
    # 3. Si la lista falló, probamos 'a la fuerza' el gemini-pro que casi siempre está
    return "gemini-pro"

# --- INICIALIZACIÓN ---
if "modelo_activo" not in st.session_state:
    with st.spinner("🔍 Buscando el mejor cerebro disponible..."):
        st.session_state["modelo_activo"] = get_best_model()

st.title("🛡️ DocuMind: Modo Robusto")
st.caption(f"Conectado a: **{st.session_state['modelo_activo']}**")

# --- LÓGICA DE PDF ---
pdf_files = st.file_uploader("Sube tus documentos", type=['pdf'], accept_multiple_files=True)

if pdf_files:
    if st.button("Procesar"):
        text = ""
        for pdf in pdf_files:
            reader = PdfReader(pdf)
            for page in reader.pages:
                text += page.extract_text() or ""
        st.session_state['text'] = text
        st.success("PDFs leídos.")

# --- CHAT ---
if 'text' in st.session_state:
    prompt = st.chat_input("Pregunta...")
    if prompt:
        with st.chat_message("user"): st.write(prompt)
        with st.chat_message("assistant"):
            try:
                # Usamos el modelo que sabemos que funciona
                model = genai.GenerativeModel(st.session_state["modelo_activo"])
                res = model.generate_content(f"Contexto: {st.session_state['text']}\n\nPregunta: {prompt}")
                st.write(res.text)
            except Exception as e:
                st.error(f"Error generando respuesta: {e}")
                st.info("Intenta recargar la página para buscar otro modelo.")
