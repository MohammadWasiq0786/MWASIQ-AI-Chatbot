import streamlit as st
import os
from dotenv import load_dotenv
from ui import setup_ui, display_chat_messages
from utils import (
    load_vectorstore,
    get_ai_response,
    extract_text_from_file,
    whisper_transcribe,
    elevenlabs_tts,
)

load_dotenv()
EURI_API_KEY = os.getenv("EURI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")


VECTOR_STORE_DIR = "vectorstore"
VECTOR_STORE_PATH = os.path.join(VECTOR_STORE_DIR, "company_vectorstore")
os.makedirs(VECTOR_STORE_DIR, exist_ok=True)
os.makedirs("uploads", exist_ok=True)


for key, default in [
    ("chat_history", []),
    ("conversation_history", []),
    ("vectorstore", None),
    ("uploaded_files", []),
    ("knowledge_updated", False),
    ("user_input", ""),
    ("recording_state", "ready"),
    ("speech_text", ""),
]:
    if key not in st.session_state:
        st.session_state[key] = default


def reset_chat():
    st.session_state.chat_history = []
    st.session_state.conversation_history = []
    st.session_state.user_input = ""
    st.rerun()


def remove_file(index):
    st.session_state.uploaded_files.pop(index)
    st.session_state.knowledge_updated = True
    st.rerun()


def start_recording():
    st.session_state.recording_state = "listening"
    st.rerun()


def record_and_transcribe():
    status_area = st.empty()
    try:
        status_area.markdown("Listening...", unsafe_allow_html=True)
        transcript = whisper_transcribe()
        st.session_state.user_input = transcript
        status_area.markdown('Done! Click "Send" to submit.', unsafe_allow_html=True)
        st.session_state.recording_state = "ready"
    except Exception as e:
        status_area.error(f"Error: {e}")
        st.session_state.recording_state = "ready"


def send_query():
    if st.session_state.user_input:
        query = st.session_state.user_input
        st.session_state.chat_history.append({"role": "user", "content": query})
        language_code = st.session_state.get("language_code", "en")

        with st.spinner("Thinking..."):
            answer, sources = get_ai_response(query, lang=language_code)
            audio_file = elevenlabs_tts(answer, lang=language_code) if answer else None

            st.session_state.chat_history.append(
                {
                    "role": "assistant",
                    "content": answer,
                    "audio": audio_file,
                    "sources": sources,
                }
            )

        st.session_state.user_input = ""
        st.rerun()


def main():
    setup_ui(
        reset_chat=reset_chat,
        remove_file=remove_file,
        extract_text_from_file=extract_text_from_file,
    )

    # Display the Euron logo
    # st.image(
    #     "/Users/myhome/AI_projects/customer supprot chatbog/euron (1).jpg", width=200
    # )

    st.title("MWASIQ AI Chatbot")
    st.markdown("Ask questions about Euron's products, services, or policies")

    chat_container = st.container()
    with chat_container:
        display_chat_messages()

    st.markdown("### Ask a Question")
    col1, col2, col3 = st.columns([6, 1, 1])

    with col1:
        st.session_state.user_input = st.text_input(
            "Type your question here...",
            value=st.session_state.user_input,
            label_visibility="collapsed",
        )

    with col2:
        if st.session_state.recording_state == "ready":
            if st.button("🎤", help="Click to speak"):
                start_recording()
        else:
            record_and_transcribe()

    with col3:
        if st.button("Send"):
            send_query()

    with st.expander("How to use MWASIQ AI Chatbot", expanded=False):
        st.markdown("""
        ### Instructions
        1. Ask questions by typing or speaking.
        2. Select text from responses as needed.
        3. Change language settings in the sidebar.
        4. Upload documents to update AI knowledge.
        5. Reset the chat anytime from the sidebar.
        """)


if __name__ == "__main__":
    main()
