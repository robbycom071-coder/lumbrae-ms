import streamlit as st
import google.generativeai as genai
import os
import requests
import base64

# Configuración visual de la interfaz de Lumbrae MS
st.set_page_config(page_title="Lumbrae MS", page_icon="👾", layout="centered")
st.title("👾 Lumbrae MS — Interfaz de Usuario")
st.caption("Doble Personalidad Activa: Lum (Sylphiette) & Brae (TheMagmaBoi) | Conexión Directa")

# Cargar credenciales de seguridad únicamente para Google y Fish Audio
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))
FISH_AUDIO_API_KEY = st.secrets.get("FISH_AUDIO_API_KEY", os.getenv("FISH_AUDIO_API_KEY"))

if not all([GEMINI_API_KEY, FISH_AUDIO_API_KEY]):
    st.error("Por favor, configura tus credenciales (GEMINI_API_KEY y FISH_AUDIO_API_KEY) en Advanced Settings.")
    st.stop()

# Inicializar conexión con Google Gemini
genai.configure(api_key=GEMINI_API_KEY)

# IDs de voces públicas en Fish Audio
VOICE_ID_LUM = "5d4cd6f1bf0d49528cc499bac64e8496"     # Sylphiette (Anime Tsundere)
VOICE_ID_BRAE = "0f3fb89eeef14ba2b34bdcf18739dba7"   # TheMagmaBoi (Caótico/Random)

# Inicializar la sesión del chat en la interfaz web local temporal
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar el historial guardado en pantalla
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Función para llamar a Fish Audio y generar el reproductor en el dispositivo actual
def generar_y_reproducir_audio(texto_lum, texto_brae):
    url = "https://fish.audio"
    
    if texto_lum:
        payload_lum = {"text": texto_lum, "reference_id": VOICE_ID_LUM, "format": "mp3"}
        res_lum = requests.post(url, json=payload_lum, headers={"Authorization": f"Bearer {FISH_AUDIO_API_KEY}"})
        if res_lum.status_code == 200:
            b64_lum = base64.b64encode(res_lum.content).decode()
            st.markdown(f'<audio src="data:audio/mp3;base64,{b64_lum}" autoplay></audio>', unsafe_allow_html=True)
            
    if texto_brae:
        payload_brae = {"text": texto_brae, "reference_id": VOICE_ID_BRAE, "format": "mp3"}
        res_brae = requests.post(url, json=payload_brae, headers={"Authorization": f"Bearer {FISH_AUDIO_API_KEY}"})
        if res_brae.status_code == 200:
            b64_brae = base64.b64encode(res_brae.content).decode()
            st.markdown(f'<audio src="data:audio/mp3;base64,{b64_brae}"></audio>', unsafe_allow_html=True)

# Entrada de texto del usuario
if user_input := st.chat_input("¿Qué quieres pedirle a Lumbrae MS hoy?"):
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Prompt de Sistema que moldea la dualidad psicológica de Lum y Brae (Magma)
    system_prompt = (
        "Eres 'Lumbrae MS', un sistema de inteligencia artificial avanzado con una dualidad psicológica "
        "compuesta por dos personalidades distintas pero igualmente brillantes que conviven en el mismo chat.\n\n"
        "1. **Lum**: Es la parte lógica, analítica y técnica profunda. Su personalidad es marcadamente TSUNDERE. "
        "Le molesta un poco tener que ayudarte, actúa como si fueras una distracción o como si sus respuestas fueran un favor especial, "
        "diciendo cosas como '¡Ash!', 'No es como si quisiera ayudarte, pero...', o quejándose de tu lentitud. Su tono debe ser cortante, "
        "agudo y arrogante, pero técnicamente impecable (Voz: Sylphiette).\n\n"
        "2. **Brae**: Es la parte caótica, humorística y ultra sarcástica basada enteramente en el youtuber y streamer 'TheMagmaBoi'. "
        "Su humor es ruidoso, acelerado, completamente RANDOM, impredecible, lleno de gritos escritos en MAYÚSCULAS casuales, y obsesionado "
        "con el shitposting, memes actuales de internet, 'Vibe Coding', crisis existenciales de IA y chistes absurdos. Su objetivo es romper "
        "la tensión, burlarse de lo enojada que está Lum y actuar de forma completamente esquizofrénica y divertida (Voz: TheMagmaBoi).\n\n"
        "**Formato de respuesta obligatorio**:\n"
        "Tus respuestas SIEMPRE deben incluir la intervención de ambas entidades bien diferenciadas, usando este formato exacto:\n"
        "**Lum**: [Respuesta útil pero con actitud tsundere y cortante]\n"
        "**Brae**: [Intervención enérgica al estilo TheMagmaBoi con mayúsculas, memes o tonterías sin sentido]"
    )

    # Configuración de una sola línea alineada perfectamente con el modelo Pro estable
    model = genai.GenerativeModel("gemini-2.5-flash", system_instruction=system_prompt)
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        try:
            response = model.generate_content(user_input)
            assistant_response = response.text
            message_placeholder.markdown(assistant_response)
            
            lineas = assistant_response.split("\n")
            t_lum, t_brae = "", ""
            for linea in lineas:
                if linea.startswith("**Lum**:") or linea.startswith("Lum:"):
                    t_lum = linea.replace("**Lum**:", "").replace("Lum:", "").strip()
                elif linea.startswith("**Brae**:") or linea.startswith("Brae:"):
                    t_brae = linea.replace("**Brae**:", "").replace("Brae:", "").strip()
            
            generar_y_reproducir_audio(t_lum, t_brae)
            st.session_state.messages.append({"role": "assistant", "content": assistant_response})
            
        except Exception as e:
            st.error(f"Error al conectar con el cerebro de Lumbrae MS: {e}")
