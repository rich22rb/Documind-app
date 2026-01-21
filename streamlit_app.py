import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader

st.set_page_config(page_title="DocuMind - Universal", page_icon="🤖")

st.title("🤖 DocuMind: Selector Automático")

# 1. Tu API Key
api_key = st.text_input("Pega tu API Key:", type="password")

if api_key:
    # 2. Configurar y Buscar Modelos Disponibles
    try:
        genai.configure(api_key=api_key)
        # Pedimos la lista real a Google
        all_models = genai.list_models()
        
        # Filtramos solo los que sirven para chatear (generateContent)
        my_models = [m.name for m in all_models if 'generateContent' in m.supported_generation_methods]
        
        if not my_models:
            st.error("Tu API Key es válida, pero Google dice que no tienes acceso a ningún modelo. ¿Es una Key nueva?")
        else:
            # 3. ¡Aquí está la magia! Un selector con lo que SÍ funciona
            selected_model = st.selectbox("Elige un modelo disponible:", my_models)
            st.success(f"Conectado a: {selected_model}")
            
            # --- Lógica de PDF y Chat ---
            pdf_file = st.file_uploader("Sube tu PDF", type=['pdf'])
            
            if pdf_file and st.button("Procesar PDF"):
                reader = PdfReader(pdf_file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() or ""
                st.session_state['text'] = text
                st.info("PDF Leído. Pregunta abajo.")

            if 'text' in st.session_state:
                question = st.text_input("Pregunta:")
                if question:
                    model = genai.GenerativeModel(selected_model)
                    response = model.generate_content(f"Contexto: {st.session_state['text']} \n\n Pregunta: {question}")
                    st.write(response.text)

    except Exception as e:
        st.error(f"Error de conexión: {e}")