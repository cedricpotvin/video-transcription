import streamlit as st
import whisper
import tempfile
import os
import requests
import urllib.parse  # For parsing query parameters

# Set up Streamlit app
st.title("Step 1: Upload The Video You Want To Convert")

# Create a placeholder for Zapier response
variation_placeholder = st.empty()

# Initialize session state for storing Zapier response
if "zapier_response" not in st.session_state:
    st.session_state.zapier_response = None

# Load Whisper model
@st.cache_resource
def load_model():
    return whisper.load_model("base")  # Use other models like 'tiny', 'large' as needed

model = load_model()

# Check if query parameters indicate a Zapier callback
query_params = st.query_params
if "variation" in query_params:
    zapier_response = urllib.parse.unquote(query_params.get("variation", [""])[0])
    st.session_state.zapier_response = zapier_response
    st.experimental_set_query_params()  # Clear query params after processing

# Display Zapier response if received
if st.session_state.zapier_response:
    variation_placeholder.text_area("Variation from Zapier", st.session_state.zapier_response, height=300)

# File uploader
uploaded_file = st.file_uploader("Upload an MP4 file", type=["mp4"])

if uploaded_file is not None:
    # Save the file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
        temp_file.write(uploaded_file.read())
        temp_filename = temp_file.name

    # Perform transcription
    st.info("Transcribing audio...")
    result = model.transcribe(temp_filename)

    # Display result
    st.success("Transcription complete!")
    transcription_text = result["text"]
    st.text_area("Transcription", transcription_text, height=300)

    # Clean up temporary file
    os.remove(temp_filename)

    # Add a "Create Variations" button
    if st.button("Create Variations"):
        st.info("Sending transcription to Zapier...")
        zapier_webhook_url = "https://hooks.zapier.com/hooks/catch/6652482/2z9cojg/"

        # Append callback URL to be sent to Zapier
        callback_url = "https://video-transcription-vertex.streamlit.app/?variation={}"
        response = requests.post(zapier_webhook_url, json={"transcription": transcription_text, "callback_url": callback_url})

        if response.status_code == 200:
            st.success("Transcription sent successfully! Waiting for Zapier to respond...")
        else:
            st.error(f"Failed to send transcription. Error: {response.status_code}")
