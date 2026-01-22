import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import time

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="DocuMind AI", page_icon="⚡", layout="centered")

# --- AUTENTICACIÓN ---
try:
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
    else:
        # Fallback por si no han configurado secretos
        api_key = st.text_input("🔑 API Key requerida:", type="password")
        if not api_key: st.stop()
    
    genai.configure(api_key=api_key)
except Exception as e:
    st.error(f"Error de Configuración: {e}")
    st.stop()

# --- FUNCIÓN INTELIGENTE DE SELECCIÓN DE MODELO ---
def get_working_model():
    """Busca qué modelo está disponible para esta API Key"""
    lista_preferencia = [
        "gemini-1.5-flash", 
        "gemini-1.5-flash-latest", 
        "gemini-1.5-pro",
        "gemini-pro"
    ]
    
    try:
        # Preguntamos a Google qué modelos ve la llave
        available_models = [m.name.replace("models/", "") for m in genai.list_models()]
        
        # Buscamos el mejor disponible
        for modelo in lista_preferencia:
            if modelo in available_models:
                return modelo
        
        # Si no encuentra coincidencia exacta, devuelve el primero que genere texto
        return available_models[0]
        
    except Exception:
        # Si falla el listado, forzamos el flash estándar
        return "gemini-1.5-flash"

# --- INTERFAZ ---
st.title("⚡ DocuMind")

# Selección automática (Invisible para el usuario, pero robusta)
if "modelo_actual" not in st.session_state:
    with st.spinner("Conectando con el cerebro de Google..."):
        st.session_state["modelo_actual"] = get_working_model()

modelo_usado = st.session_state["modelo_actual"]
st.caption(f"🟢 Conectado exitosamente a: **{modelo_usado}**")

st.divider()

# --- LÓGICA DE PDF Y CHAT ---
pdf_files = st.file_uploader("Sube tus documentos", type=['pdf'], accept_multiple_files=True)

if pdf_files:
    if st.button(f"Procesar {len(pdf_files)} Archivos"):
        with st.spinner("Leyendo..."):
            text = ""
            for pdf in pdf_files:
                reader = PdfReader(pdf)
                for page in reader.pages:
                    text += page.extract_text() or ""
            st.session_state['text'] = text
            st.success("¡Listo! Pregunta abajo.")

if 'text' in st.session_state:
    prompt = st.chat_input("Escribe tu pregunta...")
    if prompt:
        with st.chat_message("user"):
            st.write(prompt)
            
        with st.chat_message("assistant"):
            try:
                model = genai.GenerativeModel(modelo_usado)
                res = model.generate_content(f"Contexto: {st.session_state['text']}\n\nPregunta: {prompt}")
                st.write(res.text)
            except Exception as e:
                st.error(f"Error: {e}")
