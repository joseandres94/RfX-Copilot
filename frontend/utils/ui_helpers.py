import os
import streamlit as st
import requests

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

# Define helper functions
def api_get(path:str, data=None, files=None, **kwargs):
    url = f"{BACKEND_URL}{path}"
    return st.session_state.http.get(url, data=data, files=files,timeout=kwargs.pop("timeout", 20), **kwargs)


def api_post(path:str, data=None, files=None, **kwargs):
    url = f"{BACKEND_URL}{path}"
    return st.session_state.http.post(url, data=data, files=files, timeout=kwargs.pop("timeout", 90), **kwargs)


def check_backend() -> None:
    try:
        r = api_get("/health")
        r.raise_for_status()

    except requests.exceptions.HTTPError as e:
        detail = None
        if e.response is not None:
            try:
                detail=e.response.json()
            except Exception:
                detail=e.response.text
        st.error(f"Couldn't connect with backend (HTTP): {detail or e}")
        st.stop()

    except Exception as e:
        st.error(f"Couldn't connect with backend: {e}")
        st.stop()


def render_language_selector() -> None:
    """Render a language toggle button in the top right corner."""
    # Initialize language if not set
    if "language" not in st.session_state:
        st.session_state.language = "English"
    
    # Get current language and determine button text
    current_lang = st.session_state.language
    button_text = "EN" if current_lang == "English" else "SV"
    
    # Create columns to push button to the right side
    # Use a large ratio to push the button to the right
    _, col_right = st.columns([0.9, 0.1])
    
    with col_right:
        # Create the toggle button
        if st.button(button_text, key="lang_toggle", use_container_width=True):
            # Toggle between languages
            if current_lang == "English":
                st.session_state.language = "Svenska"
            else:
                st.session_state.language = "English"
            st.rerun()