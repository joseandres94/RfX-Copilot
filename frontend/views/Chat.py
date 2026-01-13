import os
import time
from uuid import uuid4
from dotenv import load_dotenv
import streamlit as st

# Import functions
from utils.ui_helpers import api_post, api_get
from utils.i18n import t

import logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

# Pipeline step mapping for progress display
PIPELINE_STEPS = {
    "ingestion": {"order": 1, "label": "Parsing document"},
    "deal_analyzer": {"order": 2, "label": "Extracting Deal Intelligence"},
    "summarizer": {"order": 3, "label": "Generating Summary"},
    "solution_architect": {"order": 4, "label": "Creating Demo Proposal"},
    "engagement_manager": {"order": 5, "label": "Analyzing Gaps"},
    "completed": {"order": 5, "label": "Completed"}
}
TOTAL_STEPS = 5


def upload_and_start_pipeline(file, session_id: str, language: str):
    """Upload file and start pipeline processing."""
    try:
        files = {"file": file}
        data = {"session_id": session_id, "language": language}
        
        response = api_post("/deals", data=data, files=files)
        response.raise_for_status()
        
        #deal_id = "d7eeb0dd-9253-45de-82b5-41f0f2673b95"
        deal_id = response.json()["deal_id"]
        st.session_state.deal_id = deal_id
        st.session_state.pipeline_active = True
        st.session_state.last_event_id = 0
        st.session_state.outputs_shown = set()  # Track which outputs we've displayed
        
        return deal_id
        
    except Exception as e:
        st.error(f"Error uploading file: {e}")
        return None


def poll_pipeline_status():
    """Poll the deal status and update session state."""
    if not st.session_state.get("deal_id"):
        return None
    
    try:
        response = api_get(
            f"/deals/{st.session_state.deal_id}",
            params={"since_event_id": st.session_state.get("last_event_id", 0)}
        )
        response.raise_for_status()
        data = response.json()
        
        # Update last event ID
        if data["events"]:
            st.session_state.last_event_id = max([e["id"] for e in data["events"]])
        
        return data
        
    except Exception as e:
        logger.error(f"Error polling status: {e}")
        return None


def render_pipeline_progress(status_data):
    """Render pipeline progress as a chat message."""
    status = status_data["status"]
    current_step = status_data["current_step"]
    
    if status == "processing":
        step_info = PIPELINE_STEPS.get(current_step, {"order": 0, "label": "Processing"})
        step_number = step_info["order"]
        step_label = step_info["label"]
        
        # Find latest event message
        latest_message = f"({step_number}/{TOTAL_STEPS}) {step_label}..."
        if status_data["events"]:
            last_event = status_data["events"][-1]
            # Use the event message if it's more descriptive
            if last_event["message"]:
                latest_message = f"({step_number}/{TOTAL_STEPS}) {last_event['message']}"
        
        # Show as info box
        st.info(latest_message)
        
    elif status == "ready":
        st.success("✅ Pipeline completed! You can now ask questions about your RfX.")
        st.session_state.pipeline_active = False
        
    elif status == "error":
        error_msg = status_data.get("error_message", "Unknown error")
        st.error(f"❌ Pipeline failed: {error_msg}")
        st.session_state.pipeline_active = False


def display_pipeline_outputs(status_data):
    """Display markdown outputs as chat messages when they become available."""
    outputs_shown = st.session_state.get("outputs_shown", set())
    
    # Check and display DIC (Deal Intelligence Card)
    if status_data.get("dic_available") and "dic" not in outputs_shown:
        dic_markdown = status_data.get("dic_markdown", "")
        
        if dic_markdown:
            st.session_state.chat.append({
                "id": str(uuid4()),
                "role": "assistant",
                "type": "output",
                "output_type": "dic",
                "title": "📊 Deal Intelligence Card Generated",
                "intro": "I've analyzed your RfX and created a comprehensive Deal Intelligence Card.",
                "content": dic_markdown,
                "stage": "output"
            })
        outputs_shown.add("dic")
    
    # Check and display Demo Brief
    if status_data.get("demo_brief_available") and "demo_brief" not in outputs_shown:
        demo_brief_markdown = status_data.get("demo_brief_markdown", "")
        
        if demo_brief_markdown:
            st.session_state.chat.append({
                "id": str(uuid4()),
                "role": "assistant",
                "type": "output",
                "output_type": "demo_brief",
                "title": "🏗️ Demo Brief Created",
                "intro": "I've designed a demo proposal based on your requirements.",
                "content": demo_brief_markdown,
                "stage": "output"
            })
        outputs_shown.add("demo_brief")
    
    # Check and display Gap Analysis
    if status_data.get("gaps_available") and "gaps" not in outputs_shown:
        gaps_markdown = status_data.get("gaps_markdown", "")
        
        # Extract stats from latest event if available
        intro = "I've identified potential gaps and risks in covering your requirements."
        
        # Look for gap stats in events to enhance intro
        for event in reversed(status_data.get("events", [])):
            if event.get("step") == "engagement_manager" and event.get("payload"):
                total = event["payload"].get("total_gaps", 0)
                high = event["payload"].get("high_severity_gaps", 0)
                if total > 0:
                    intro = f"Identified {total} gap(s)"
                    if high > 0:
                        intro += f" ({high} high severity)"
                    intro += ". Review the detailed analysis below."
                break
        
        if gaps_markdown:
            st.session_state.chat.append({
                "id": str(uuid4()),
                "role": "assistant",
                "type": "output",
                "output_type": "gaps",
                "title": "🎯 Gap Analysis Complete",
                "intro": intro,
                "content": gaps_markdown,
                "stage": "output"
            })
        outputs_shown.add("gaps")
    
    st.session_state.outputs_shown = outputs_shown


def process_text(text_message: str, type: str):
    """Function that handles API call for text generation by LLM."""
    try:
        # Call API
        payload = {
            "session_id": st.session_state.session_id,
            "text_message": text_message,
            "language": st.session_state.language
        }
        
        # Include deal_id if available
        if "deal_id" in st.session_state and st.session_state.deal_id:
            payload["deal_id"] = st.session_state.deal_id
        
        response = api_post("/chat", json=payload)
        response.raise_for_status()

        # Extract response and transform to frontend format
        backend_response = response.json()
        chat_message = {
            "id": str(uuid4()),
            "role": "assistant",
            "type": "text",
            "content": backend_response.get("answer", ""),
            "stage": backend_response.get("stage", "qa")
        }
        st.session_state.chat.append(chat_message)

    except Exception as e:
        error_message = str(e)
        
        # Check if error is due to deal not being ready
        if "409" in error_message or "processing" in error_message.lower():
            st.session_state.chat.append({
                "id": str(uuid4()),
                "role": "assistant",
                "type": "text",
                "content": "⚠️ The RfX is still being processed. Please wait a moment...",
                "stage": "error"
            })
        else:
            st.session_state.chat.append({
                "id": str(uuid4()),
                "role": "assistant",
                "type": "text",
                "content": f"❌ Error: {e}",
                "stage": "error"
            })


def process_audio(audio_input) -> str:
    """Function that handles API call for Speech-to-Text generation."""
    # Extract content from audio
    blob = audio_input.getvalue()
    fname = getattr(audio_input, "name", "recording.wav")
    mime = getattr(audio_input, "type", "audio/wav")

    # Avoid processing same audio
    sig = (len(blob), fname)
    if st.session_state.get("last_audio_sig") != sig or not st.session_state.get("last_audio_sig"):
        st.session_state["last_audio_sig"] = sig
        try:
            # Call API
            files = {"file": (fname, blob, mime)}
            response = api_post("/stt", files=files)
            response.raise_for_status()
            return response.json().get("transcription", "").strip()
        except Exception as e:
            st.error(f"Error transcribing audio: {e}")
            return ""


def generate_tts(session_id: str, text_message: str, language: str) -> bytes:
    """Function that handles API call for Text-to-Speech generation."""
    try:
        # Call API
        payload = {
            "session_id": session_id,
            "text_message": text_message,
            "language": language
        }
        response = api_post("/tts", json=payload)
        response.raise_for_status()
        return response.content
    except Exception as e:
        st.error(f"Error generating audio: {e}")
        return None


def main():
    """Main function for the Chat page."""
    st.set_page_config(page_title="RfX Copilot", page_icon="💬", layout="wide")
    
    # Header
    st.title("💬 RfX Copilot")
    st.markdown("*Powered by Tacton AI*")
    
    # Initialize session state
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid4())
    if "language" not in st.session_state:
        st.session_state.language = "English"
    if "chat" not in st.session_state:
        st.session_state.chat = []
    if "deal_id" not in st.session_state:
        st.session_state.deal_id = None
    if "pipeline_active" not in st.session_state:
        st.session_state.pipeline_active = False
    if "tts_played" not in st.session_state:
        st.session_state.tts_played = {}
    if "last_event_id" not in st.session_state:
        st.session_state.last_event_id = 0
    if "outputs_shown" not in st.session_state:
        st.session_state.outputs_shown = set()
    
    # Sidebar
    with st.sidebar:
        st.caption(f"Session ID: {st.session_state.session_id[:8]}...")
        
        # Show deal info if connected
        if st.session_state.deal_id:
            st.success(f"📊 Deal: {st.session_state.deal_id[:8]}...")
        
        st.divider()
        
        # Language selector
        language = st.selectbox(
            "Language",
            options=["English", "Svenska"],
            index=0 if st.session_state.language == "English" else 1
        )
        st.session_state.language = language
        
        st.divider()
        
        # Restart conversation
        if st.button("🔄 New Conversation", use_container_width=True):
            st.session_state.chat = []
            st.session_state.deal_id = None
            st.session_state.pipeline_active = False
            st.session_state.session_id = str(uuid4())
            st.session_state.last_event_id = 0
            st.session_state.outputs_shown = set()
            st.rerun()
    
    # Check if file was uploaded from Home and auto-start
    if "file" in st.session_state and st.session_state.file and not st.session_state.deal_id:
        with st.spinner("Uploading RfX..."):
            deal_id = upload_and_start_pipeline(
                st.session_state.file,
                st.session_state.session_id,
                st.session_state.language
            )
            if deal_id:
                # Add welcome message
                st.session_state.chat.append({
                    "id": str(uuid4()),
                    "role": "assistant",
                    "type": "text",
                    "content": f"👋 Welcome! I'm processing your RfX document: **{st.session_state.file.name}**\n\nI'll analyze the requirements and create a comprehensive deal brief. This will take a few moments...",
                    "stage": "welcome"
                })
                st.session_state.file = None
                st.rerun()
    
    # Main chat area
    chat_container = st.container(border=False, height=500)
    
    with chat_container:
        # Display chat messages
        for msg in st.session_state.chat:
            with st.chat_message(msg["role"]):
                # For output messages (DIC, Demo Brief, Gaps), render with special formatting
                if msg.get("type") == "output" and msg.get("output_type"):
                    # Display title and intro
                    st.markdown(f"**{msg['title']}**")
                    st.markdown(msg['intro'])
                    st.markdown("---")
                    
                    # Display content in expander for better UX with long content
                    content_length = len(msg.get("content", ""))
                    
                    if content_length > 2000:  # Long content - use expander
                        with st.expander("📄 View Full Report", expanded=True):
                            st.markdown(msg["content"])
                    else:  # Short content - display directly
                        st.markdown(msg["content"])
                        
                # For regular messages
                elif msg.get("content"):
                    st.write(msg["content"])
                
                # Display TTS audio for assistant voice messages
                if msg["role"] == "assistant" and msg.get("type") == "audio":
                    if msg["id"] not in st.session_state.tts_played:
                        with st.spinner("🎙️ Generating audio..."):
                            audio_bytes = generate_tts(
                                session_id=msg["id"],
                                text_message=str(msg["content"]),
                                language=st.session_state.language
                            )
                        if audio_bytes:
                            st.audio(audio_bytes, format="audio/wav", autoplay=True)
                            st.session_state.tts_played[msg["id"]] = audio_bytes
                    else:
                        st.audio(st.session_state.tts_played[msg["id"]], format="audio/wav", autoplay=False)
        
        # Show pipeline progress if active
        if st.session_state.pipeline_active:
            status_data = poll_pipeline_status()
            
            if status_data:
                # Display outputs as they become available
                display_pipeline_outputs(status_data)
                
                # Show current progress
                render_pipeline_progress(status_data)
                
                # Auto-refresh if still processing
                if status_data["status"] == "processing":
                    time.sleep(2)
                    st.rerun()
    
    # Input section (disabled during pipeline processing)
    if st.session_state.pipeline_active:
        st.info("⏳ Pipeline is processing... Chat will be enabled when complete.")
    else:
        # Get pending request
        pending = st.session_state.get("pending_request")
        
        # Process pending request
        if pending:
            with st.spinner("🤔 Thinking..."):
                process_text(pending["text"], type=pending["type"])
                st.session_state["pending_request"] = None
                st.rerun()
        
        # Input controls
        col1, col2 = st.columns([0.75, 0.25])
        
        with col1:
            text_message = st.chat_input("Ask me anything about the RfX...")
            if text_message:
                msg_id = str(uuid4())
                st.session_state.chat.append({
                    "id": msg_id,
                    "role": "user",
                    "type": "text",
                    "content": text_message,
                    "stage": "input"
                })
                st.session_state["pending_request"] = {
                    "message_id": msg_id,
                    "type": "text",
                    "text": text_message
                }
                st.rerun()
        
        with col2:
            audio_input = st.audio_input("🎤", key="voice_mic", label_visibility="collapsed")
            if audio_input:
                msg_id = str(uuid4())
                transcription = process_audio(audio_input)
                if transcription:
                    st.session_state.chat.append({
                        "id": msg_id,
                        "role": "user",
                        "type": "audio",
                        "content": transcription,
                        "stage": "input"
                    })
                    st.session_state["pending_request"] = {
                        "message_id": msg_id,
                        "type": "audio",
                        "text": transcription
                    }
                    st.rerun()


if __name__ == "__main__":
    main()
