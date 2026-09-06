import streamlit as st
import os
import base64
from dotenv import load_dotenv
from groq import Groq
import speech_recognition as sr
from gtts import gTTS


# ------------------ Load API Key ------------------

load_dotenv(override=True)

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

st.set_page_config(
    page_title="VoiceDeskAI",
    layout="wide"
)


# ------------------ Text To Speech ------------------

def speak(text):

    try:

        lang = "hi" if any(
            "\u0900" <= c <= "\u097F"
            for c in text
        ) else "en"

        tts = gTTS(
            text=text,
            lang=lang
        )

        tts.save("response.mp3")

        with open("response.mp3", "rb") as audio:

            audio_bytes = audio.read()

        st.audio(
            audio_bytes,
            format="audio/mpeg"
        )

    except Exception as e:

        st.error(
            f"Voice Error: {e}"
        )


# ------------------ Voice Input ------------------

def listen():

    recognizer = sr.Recognizer()

    try:

        with sr.Microphone() as source:

            st.info("🎤 Listening...")

            recognizer.adjust_for_ambient_noise(
                source,
                duration=1
            )

            audio = recognizer.listen(
                source,
                timeout=15,
                phrase_time_limit=15
            )

        text = recognizer.recognize_google(
            audio
        )

        return text

    except sr.WaitTimeoutError:

        st.warning(
            "⏱️ No voice detected. Please speak again."
        )

        return None

    except sr.UnknownValueError:

        st.warning(
            "❌ Could not understand your voice."
        )

        return None

    except Exception as e:

        st.error(
            f"Microphone Error: {e}"
        )

        return None


# ------------------ AI Response ------------------

def get_ai_response(user_text, language):

    prompt = user_text

    if language == "Hindi":

        prompt = (
            "Reply only in Hindi.\n\n"
            + user_text
        )

    elif language == "Hindi + English":

        prompt = (
            "Reply in a natural mix of Hindi and English.\n\n"
            + user_text
        )

    response = client.chat.completions.create(

        model="llama-3.1-8b-instant",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content


# ------------------ Session State ------------------

if "chat_history" not in st.session_state:

    st.session_state.chat_history = []


# ------------------ Sidebar ------------------

st.sidebar.title("🎙️ VoiceDeskAI")

st.sidebar.write("Version 2.0")

voice_input = st.sidebar.checkbox(
    "Voice Input",
    value=True
)

ai_chat = st.sidebar.checkbox(
    "AI Chat",
    value=True
)

voice_output = st.sidebar.checkbox(
    "Voice Output",
    value=True
)

show_history = st.sidebar.checkbox(
    "Chat History",
    value=True
)

language = st.sidebar.selectbox(
    "Language",
    [
        "English",
        "Hindi",
        "Hindi + English"
    ]
)


# ------------------ Main UI ------------------

st.title(
    "🤖 Your Personal AI Voice Assistant"
)

st.write(
    "Ask questions using text or your voice."
)


# ------------------ Text Input ------------------

user_input = st.text_area(
    "Type your question"
)


# ------------------ Ask AI ------------------

if ai_chat and st.button("Ask AI"):

    if user_input.strip():

        with st.spinner("Thinking..."):

            try:

                answer = get_ai_response(
                    user_input,
                    language
                )

                st.success("AI Response")

                st.write(answer)

                if voice_output:

                    speak(answer)

                st.session_state.chat_history.append(
                    ("You", user_input)
                )

                st.session_state.chat_history.append(
                    ("AI", answer)
                )

            except Exception as e:

                st.error(
                    f"AI Error: {e}"
                )

    else:

        st.warning(
            "Please enter a question."
        )


# ------------------ Voice Input ------------------

if voice_input and st.button("🎤 Speak"):

    voice_text = listen()

    if voice_text:

        st.success("You said:")

        st.write(voice_text)

        with st.spinner("Thinking..."):

            try:

                answer = get_ai_response(
                    voice_text,
                    language
                )

                st.success("AI Response")

                st.write(answer)

                if voice_output:

                    speak(answer)

                st.session_state.chat_history.append(
                    ("You", voice_text)
                )

                st.session_state.chat_history.append(
                    ("AI", answer)
                )

            except Exception as e:

                st.error(
                    f"AI Error: {e}"
                )


# ------------------ Chat History ------------------

if show_history:

    st.sidebar.subheader(
        "💬 Chat History"
    )

    if len(st.session_state.chat_history) == 0:

        st.sidebar.write(
            "No chats yet."
        )

    else:

        for sender, message in st.session_state.chat_history:

            st.sidebar.markdown(
                f"**{sender}:** {message}"
            )

    if st.sidebar.button("🗑 Clear Chat"):

        st.session_state.chat_history = []

        st.rerun()