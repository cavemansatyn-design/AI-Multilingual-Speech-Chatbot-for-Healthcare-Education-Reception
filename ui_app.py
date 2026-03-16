"""
Streamlit UI for Multilingual Symptom Chatbot.
Requires FastAPI backend running at http://localhost:8000
"""
import base64
import json
from typing import Optional, Dict, Any

import requests
import streamlit as st

# Streamlit compatibility: experimental_rerun was renamed to rerun in v1.27+
def _rerun() -> None:
    if hasattr(st, "rerun"):
        st.rerun()
    else:
        st.experimental_rerun()  # type: ignore


API_BASE = "http://localhost:8000"


def call_chat_text(text: str, language: str, state: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Call FastAPI /chat/text endpoint."""
    data: Dict[str, Any] = {"text": text, "language": language}
    if state is not None:
        data["state_json"] = json.dumps(state)
    resp = requests.post(f"{API_BASE}/chat/text", data=data, timeout=60)
    resp.raise_for_status()
    return resp.json()


def call_chat_audio(
    audio_bytes: bytes,
    filename: str,
    language: str,
    state: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    """Call FastAPI /chat/audio endpoint with uploaded audio."""
    files = {"audio": (filename, audio_bytes, "audio/wav")}
    data: Dict[str, Any] = {"language": language}
    if state is not None:
        data["state_json"] = json.dumps(state)
    resp = requests.post(f"{API_BASE}/chat/audio", files=files, data=data, timeout=120)
    resp.raise_for_status()
    return resp.json()


def call_generate_pdf(
    report_text: str,
    structured: Optional[Dict[str, Any]],
    patient_name: str = "",
    patient_age: str = "",
    patient_gender: str = "",
    patient_contact: str = "",
) -> bytes:
    """Call FastAPI /report/pdf endpoint and return PDF bytes."""
    payload = {
        "report_text": report_text,
        "structured": structured,
        "patient_name": patient_name,
        "patient_age": patient_age,
        "patient_gender": patient_gender,
        "patient_contact": patient_contact,
    }
    resp = requests.post(f"{API_BASE}/report/pdf", json=payload, timeout=30)
    resp.raise_for_status()
    return resp.content


def render_history() -> None:
    """Render chat history stored in session state."""
    for turn in st.session_state.history:
        with st.chat_message("user"):
            st.markdown(turn["user"])
        with st.chat_message("assistant"):
            st.markdown(turn["bot"])


def main() -> None:
    """Streamlit front-end for the multilingual chatbot."""
    st.set_page_config(
        page_title="Multilingual Symptom Chatbot",
        page_icon="🩺",
        layout="centered",
    )

    st.title("🩺 Multilingual Symptom Chatbot")
    st.markdown(
        "Describe your symptoms using **text or audio**. "
        "The assistant will ask follow‑up questions and generate a structured report."
    )

    # Sidebar: settings
    with st.sidebar:
        st.header("Settings")
        language = st.selectbox(
            "Conversation language",
            options=["en", "hi", "fr", "es", "de"],
            format_func=lambda c: {
                "en": "English",
                "hi": "Hindi",
                "fr": "French",
                "es": "Spanish",
                "de": "German",
            }[c],
            index=0,
        )
        mode = st.radio("Input type", ["Text", "Audio"], index=0)
        if st.button("Reset conversation"):
            st.session_state.state = None
            st.session_state.history = []
            st.session_state.last_report = None
            st.session_state.pdf_bytes = None
            _rerun()

    # Session state init
    if "state" not in st.session_state:
        st.session_state.state = None
    if "history" not in st.session_state:
        st.session_state.history = []
    if "last_report" not in st.session_state:
        st.session_state.last_report = None
    if "pdf_bytes" not in st.session_state:
        st.session_state.pdf_bytes = None

    # Conversation area
    render_history()

    # Show report + PDF download when we have a generated report
    if st.session_state.last_report:
        report_text = st.session_state.last_report.get("report_text", "")
        structured = st.session_state.last_report.get("structured")

        st.markdown("---")
        st.markdown("### Generated report")
        st.write(report_text)

        st.markdown("#### Download PDF summary")
        with st.expander("Patient information (optional)", expanded=False):
            p_name = st.text_input("Name", key="pdf_name")
            p_age = st.text_input("Age", key="pdf_age")
            p_gender = st.selectbox("Gender", ["", "Male", "Female", "Other"], key="pdf_gender")
            p_contact = st.text_input("Contact (phone/email)", key="pdf_contact")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Generate PDF report"):
                try:
                    pdf_bytes = call_generate_pdf(
                        report_text=report_text,
                        structured=structured,
                        patient_name=p_name or "",
                        patient_age=p_age or "",
                        patient_gender=p_gender or "",
                        patient_contact=p_contact or "",
                    )
                    st.session_state.pdf_bytes = pdf_bytes
                    _rerun()
                except requests.RequestException as exc:
                    st.error(f"Failed to generate PDF: {exc}")

        if st.session_state.pdf_bytes:
            st.download_button(
                label="Save patient-summary-report.pdf",
                data=st.session_state.pdf_bytes,
                file_name="patient-summary-report.pdf",
                mime="application/pdf",
                key="pdf_download",
            )

        st.markdown("---")

    # Input & actions
    if mode == "Text":
        prompt = st.chat_input("Describe your symptoms or answer the follow‑up question")
        if prompt:
            try:
                result = call_chat_text(prompt, language, st.session_state.state)
            except requests.RequestException as exc:
                st.error(f"Request failed: {exc}")
                return

            reply = result.get("reply") or "(no reply)"
            st.session_state.history.append({"user": prompt, "bot": reply})
            st.session_state.state = result.get("state")

            report_text = result.get("report_text")
            if report_text:
                st.session_state.last_report = {
                    "report_text": report_text,
                    "structured": result.get("structured"),
                }

            audio_b64 = result.get("audio_base64")
            if audio_b64:
                st.audio(base64.b64decode(audio_b64), format="audio/mp3")

            _rerun()

    else:
        audio_file = st.file_uploader(
            "Upload an audio file with your symptoms", type=["wav", "mp3", "m4a"]
        )
        if st.button("Send audio", type="primary"):
            if not audio_file:
                st.warning("Please upload an audio file first.")
            else:
                try:
                    audio_bytes = audio_file.read()
                    result = call_chat_audio(
                        audio_bytes,
                        audio_file.name,
                        language,
                        st.session_state.state,
                    )
                except requests.RequestException as exc:
                    st.error(f"Request failed: {exc}")
                    return

                transcribed = result.get("transcribed") or "[audio]"
                reply = result.get("reply") or "(no reply)"
                st.session_state.history.append(
                    {"user": transcribed, "bot": reply}
                )
                st.session_state.state = result.get("state")

                st.markdown(f"**Transcribed:** {transcribed}")

                report_text = result.get("report_text")
                if report_text:
                    st.session_state.last_report = {
                        "report_text": report_text,
                        "structured": result.get("structured"),
                    }

                audio_b64 = result.get("audio_base64")
                if audio_b64:
                    st.audio(base64.b64decode(audio_b64), format="audio/mp3")

                _rerun()


if __name__ == "__main__":
    main()

