import streamlit as st
import requests
import os
import numpy as np


def main():
    st.markdown("<h2></h2>", unsafe_allow_html=True)
    st.markdown(
        "<div style='text-align: center;'><h1>Music Stem Extraction</h1></div>",
        unsafe_allow_html=True,
    )
    st.markdown("<h2></h2>", unsafe_allow_html=True)
    st.markdown("<h2></h2>", unsafe_allow_html=True)

    st.markdown("<h2>Upload Audio File</h2>", unsafe_allow_html=True)
    st.divider()  # Draws a horizontal line
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["mp3", "wav", "ogg", "flac"],
        key="upload_file",
        help="Supported formats: mp3, wav, ogg, flac.",
    )
    if uploaded_file is not None:
        st.audio(uploaded_file, format="audio/wav")
    # Options
    st.markdown("<h2>Select Instruments and Model</h2>", unsafe_allow_html=True)
    st.divider()  # Draws a horizontal line

    checkboxes = {
        "vocals": st.checkbox("Vocals 🎤", key="upload_vocals"),
        "drums": st.checkbox("Drums 🥁", key="upload_drums"),
        "bass": st.checkbox("Bass 🎸", key="upload_bass"),
        "other": st.checkbox("Other 🎶", key="upload_other"),
    }
    selected_instruments = [
        instrument for instrument, checked in checkboxes.items() if checked
    ]
    selected_model = "Open-Unmix"
    # Separation
    if uploaded_file is not None:
        audio_file_path = download_uploaded_file(uploaded_file, "audio/upload")
        execute = st.button(
            "Process",
            type="primary",
            key="upload_separate_button",
            use_container_width=True,
        )
        if "executed" not in st.session_state:
            st.session_state["executed"] = False
        if execute or st.session_state.executed:
            if execute:
                st.session_state.executed = False
            if not st.session_state.executed:
                # Show processing message
                processing_message = st.empty()
                processing_message.info("Processing...")
                api_call_and_display(audio_file_path, selected_instruments)
                processing_message.empty()


def api_call_and_display(audio_file_path, selected_instruments):
    api_url = os.getenv("API_URL", "http://localhost:8000/separate_sota")
    absolute_path = os.path.abspath(audio_file_path)
    response = requests.post(url=api_url, json={"file_path": absolute_path})
    if response.status_code == 200:
        st.markdown("<h2>Results</h2>", unsafe_allow_html=True)
        display_selected_instruments(selected_instruments, response)
        st.success("Processing complete!")
    else:
        st.error("Failed to process the audio. Please try again.")


def display_selected_instruments(selected_instruments, response):
    sample_rate = response.json()["sr"]
    for stem in selected_instruments:
        # Use the full absolute path returned by the API
        stem_path = response.json()[stem]

        if not os.path.isfile(stem_path):
            st.error(f"File not found: {stem_path}")
            continue

        # Load the .npy file
        stem_array = np.load(stem_path).squeeze()
        st.text(stem)
        st.audio(stem_array, sample_rate=sample_rate)


def download_uploaded_file(uploaded_file, output_folder):
    # Check if the output folder exists, if not, create it
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    file_path = os.path.join(output_folder, "audio.mp3")  # SAME NAME ALL FILE
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path


if __name__ == "__main__":
    main()
