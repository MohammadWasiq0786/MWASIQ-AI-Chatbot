import streamlit as st


# Page configuration
def setup_ui(reset_chat, remove_file, extract_text_from_file):
    # Set page config
    st.set_page_config(page_title="MWASIQ AI Chatbot", page_icon="🤖", layout="wide")

    # Apply custom CSS
    apply_custom_css()

    # Sidebar elements
    with st.sidebar:
        st.title("MWASIQ AI Chatbot")
        st.markdown("---")

        # Language selection
        languages = {
            "English": "en",
            "Spanish": "es",
            "French": "fr",
            "German": "de",
            "Chinese": "zh-CN",
            "Japanese": "ja",
            "Hindi": "hi",
        }
        selected_language = st.selectbox(
            "Select Language", list(languages.keys()), index=0
        )
        st.session_state.language_code = languages[selected_language]

        # File upload
        st.markdown("### Add Knowledge")
        uploaded_file = st.file_uploader(
            "Upload additional documents",
            type=["pdf", "txt", "md", "html"],
            help="Upload files to enhance the AI's knowledge",
        )

        if uploaded_file:
            file_text = extract_text_from_file(uploaded_file)
            if file_text:
                file_info = {"name": uploaded_file.name, "content": file_text}
                if file_info not in st.session_state.uploaded_files:
                    st.session_state.uploaded_files.append(file_info)
                    st.session_state.knowledge_updated = True
                    st.success(f"Added {uploaded_file.name} to knowledge base")

        # Show uploaded files
        if st.session_state.uploaded_files:
            st.markdown("### Uploaded Files")
            for i, file_info in enumerate(st.session_state.uploaded_files):
                st.markdown(f"**{i + 1}. {file_info['name']}**")
                remove_button_key = f"remove_{i}"
                if st.button(f"Remove {file_info['name']}", key=remove_button_key):
                    remove_file(i)

        # Reset chat
        if st.button("Reset Chat", key="reset_chat"):
            reset_chat()


# Avatar images
def get_avatar_html(avatar_type):
    if avatar_type == "user":
        avatar_url = "https://api.dicebear.com/7.x/personas/svg?seed=user"
    else:
        avatar_url = "https://api.dicebear.com/7.x/bottts/svg?seed=techease"

    return f'<img src="{avatar_url}" alt="{avatar_type} avatar">'


# Display chat messages with selectable text
def display_chat_messages():
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            col1, col2 = st.columns([1, 9])
            with col1:
                st.markdown(
                    f'<div class="avatar">{get_avatar_html("user")}</div>',
                    unsafe_allow_html=True,
                )
            with col2:
                st.markdown(
                    f'<div class="chat-message user"><div class="message">{message["content"]}</div></div>',
                    unsafe_allow_html=True,
                )
        else:
            col1, col2 = st.columns([1, 9])
            with col1:
                st.markdown(
                    f'<div class="avatar">{get_avatar_html("bot")}</div>',
                    unsafe_allow_html=True,
                )
            with col2:
                # Make sure the text is properly escaped but still selectable
                st.markdown(
                    f'<div class="chat-message bot"><div class="message">{message["content"]}</div></div>',
                    unsafe_allow_html=True,
                )

                # Add audio playback if available
                if "audio" in message and message["audio"]:
                    st.audio(message["audio"])


# Apply custom CSS
def apply_custom_css():
    st.markdown(
        """
    <style>
        .main {
            background-color: #f5f8fa;
        }
        .stApp {
            max-width: 1200px;
            margin: 0 auto;
        }
        /* Make chat message text selectable */
        .chat-message {
            padding: 1.5rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
            display: flex;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            user-select: text !important;
            -webkit-user-select: text !important;
            -moz-user-select: text !important;
            -ms-user-select: text !important;
        }
        .chat-message.user {
            background-color: #e3f2fd;
            border-left: 5px solid #1976d2;
            color: #1565C0;
        }
        .chat-message.bot {
            background-color: #f9fbe7;
            border-left: 5px solid #7cb342;
            color: #d32f2f;
        }
        .chat-message .avatar {
            width: 20%;
        }
        .chat-message .avatar img {
            max-width: 78px;
            max-height: 78px;
            border-radius: 50%;
            object-fit: cover;
        }
        .chat-message .message {
            width: 80%;
            padding: 0 1.5rem;
            /* Ensure text is selectable */
            user-select: text !important;
            -webkit-user-select: text !important;
            -moz-user-select: text !important;
            -ms-user-select: text !important;
        }
        /* Make all text selectable */
        p, h1, h2, h3, h4, h5, h6, span, div {
            user-select: text !important;
            -webkit-user-select: text !important;
            -moz-user-select: text !important;
            -ms-user-select: text !important;
        }
        .highlighted {
            background-color: #fff9c4;
            padding: 0.2rem 0.4rem;
            border-radius: 0.25rem;
        }
        .stAudio {
            margin-top: 1rem;
        }
        .tool-button {
            border-radius: 20px !important;
            padding: 0.5em 1em !important;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1) !important;
        }
        .file-uploader {
            padding: 1rem;
            border: 2px dashed #ccc;
            border-radius: 0.5rem;
            text-align: center;
            margin-bottom: 1rem;
        }
        .language-selector {
            margin-bottom: 1rem;
        }
        .file-info {
            background-color: #e8f5e9;
            padding: 0.5rem;
            border-radius: 0.25rem;
            margin-top: 0.5rem;
        }
        .sidebar .stButton button {
            width: 100%;
            margin-bottom: 0.5rem;
        }
        /* Mic button styling */
        .mic-button {
            background-color: #1976d2;
            color: white;
            border-radius: 50%;
            width: 48px;
            height: 48px;
            line-height: 48px;
            text-align: center;
            font-size: 24px;
            cursor: pointer;
            border: none;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
        }
        .mic-button:hover {
            background-color: #1565c0;
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        }
        .mic-button.recording {
            background-color: #d32f2f;
            animation: pulse 1.5s infinite;
        }
        @keyframes pulse {
            0% {
                box-shadow: 0 0 0 0 rgba(211, 47, 47, 0.4);
            }
            70% {
                box-shadow: 0 0 0 10px rgba(211, 47, 47, 0);
            }
            100% {
                box-shadow: 0 0 0 0 rgba(211, 47, 47, 0);
            }
        }
        /* Status indicator for voice recording */
        .status-indicator {
            padding: 0.5rem;
            margin-top: 0.5rem;
            border-radius: 0.25rem;
            font-weight: bold;
            text-align: center;
        }
        .status-indicator.listening {
            background-color: #ffcdd2;
            color: #c62828;
        }
        .status-indicator.processing {
            background-color: #fff9c4;
            color: #f57f17;
        }
        .status-indicator.ready {
            background-color: #c8e6c9;
            color: #2e7d32;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )
