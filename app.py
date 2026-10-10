import streamlit as st
import google.generativeai as genai
import os
import requests
import base64

# Configuración visual de la interfaz de Lumbrae MS
st.set_page_config(page_title="Lumbrae MS", page_icon="👾", layout="centered")
st.title("👾 Lumbrae MS — Interfaz de Usuario")
st.caption("Doble Personalidad Activa: Lum (Sylphiette) & Brae (TheMagmaBoi) | Voces Separadas")

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

# Inicializar la sesión del chat local temporal
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Mostrar el historial guardado con los bloques separados visualmente
for chat in st.session_state.chat_history:
    if chat["type"] == "user":
        with st.chat_message("user"):
            st.markdown(chat["content"])
    elif chat["type"] == "assistant":
        # Recuadro de Lum
        with st.chat_message("assistant", avatar="👩‍💻"):
            st.markdown(f"**Lum**: {chat['lum_text']}")
            if chat["lum_audio"]:
                st.audio(chat["lum_audio"], format="audio/mp3")
        # Recuadro de Brae separado
        with st.chat_message("assistant", avatar="🔥"):
            st.markdown(f"**Brae**: {chat['brae_text']}")
            if chat["brae_audio"]:
                st.audio(chat["brae_audio"], format="audio/mp3")

# Función para mandar el texto al clonador y regresar el archivo MP3 real
def obtener_bytes_audio(texto, voice_id):
    if not texto:
        return None
    url = "https://fish.audio"
    payload = {"text": texto, "reference_id": voice_id, "format": "mp3"}
    headers = {"Authorization": f"Bearer {FISH_AUDIO_API_KEY}"}
    try:
        res = requests.post(url, json=payload, headers=headers)
        if res.status_code == 200:
            return res.content
    except Exception:
        pass
    return None

# Entrada de texto del usuario
if user_input := st.chat_input("¿Qué quieres pedirle a Lumbrae MS hoy?"):
    with st.chat_message("user"):
        st.markdown(user_input)
        
    # Instrucciones estrictas para que Gemini separe perfectamente los diálogos
    system_prompt = (
        "Eres 'Lumbrae MS', una IA con dos personalidades distintas que conviven en el mismo sistema.\n\n"
        "1. **Lum**: Lógica, analítica y TSUNDERE. Le molesta ayudarte, actúa como si fuera un favor especial. "
        "Usa frases como '¡Ash!', 'No es como si quisiera ayudarte...'. Tono cortante pero técnicamente impecable.\n"
        "2. **Brae**: Caótico y sarcástico al estilo del streamer 'TheMagmaBoi'. Humor ruidoso, MAYÚSCULAS casuales, "
        "memes, crisis de IA y chistes absurdos.\n\n"
        "**REGLA DE FORMATO ESTRICTA**:\n"
        "Debes responder en exactamente dos líneas limpias, una para cada uno, sin asteriscos ni emojis rebeldes antes de sus nombres. Así:\n"
        "Lum: [Texto de Lum aquí]\n"
        "Brae: [Texto de Brae aquí]"
    )

    model = genai.GenerativeModel("gemini-3.8-flash", system_instruction=system_prompt)

    try:
        response = model.generate_content(user_input)
        assistant_response = response.text
        
        # Separar los textos de Lum y Brae limpiando caracteres raros
        lineas = assistant_response.split("\n")
        t_lum, t_brae = "", ""
        for linea in lineas:
            linea_limpia = linea.replace("**", "").replace("*", "").strip()
            if linea_limpia.lower().startswith("lum:"):
                t_lum = linea_limpia[4:].strip()
            elif linea_limpia.lower().startswith("brae:"):
                t_brae = linea_limpia[5:].strip()

        # Generar los archivos de sonido de manera independiente
        audio_lum = obtener_bytes_audio(t_lum, VOICE_ID_LUM)
        audio_brae = obtener_bytes_audio(t_brae, VOICE_ID_BRAE)

        # Mostrar en pantalla el recuadro exclusivo de Lum
        with st.chat_message("assistant", avatar="👩‍💻"):
            st.markdown(f"**Lum**: {t_lum}")
            if audio_lum:
                st.audio(audio_lum, format="audio/mp3")

        # Mostrar en pantalla el recuadro exclusivo de Brae completamente aparte
        with st.chat_message("assistant", avatar="🔥"):
            st.markdown(f"**Brae**: {t_brae}")
            if audio_brae:
                st.audio(audio_brae, format="audio/mp3")

        # Guardar en el historial de la sesión actual
        st.session_state.chat_history.append({
            "type": "user",
            "content": user_input,
            "lum_text": "", "brae_text": "", "lum_audio": None, "brae_audio": None
        })
        st.session_state.chat_history.append({
            "type": "assistant",
            "lum_text": t_lum,
            "brae_text": t_brae,
            "lum_audio": audio_lum,
            "brae_audio": audio_brae
        })

    except Exception as e:
        st.error(f"Error al procesar la respuesta: {e}")
