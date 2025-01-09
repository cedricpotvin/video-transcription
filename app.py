import streamlit as st
from flask import Flask, request, jsonify
import threading
import whisper
import tempfile
import os
import requests
import urllib.parse

# Set up Streamlit app
st.title("Step 1: Upload The Video You Want To Convert")

# Placeholder for variation
variation_placeholder = st.empty()

# Initialize session state for Zapier response
if "zapier_response" not in st.session_state:
    st.session_state.zapier_response = None

# Load Whisper model
@st.cache_resource
def load_model():
    return whisper.load_model("base")  # Use other models like 'tiny', 'large' as needed

model = load_model()

# Flask app to handle POST requests
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json  # Parse JSON data from Zapier
    if "variation" in data:
        st.session_state.zapier_response = data["variation"]
        return jsonify({"message": "Variation received successfully!"}), 200
    return jsonify({"error": "Invalid data!"}), 400

# Run Flask app in a separate thread
def run_flask():
    app.run(port=5001, debug=False, use_reloader=False)

flask_thread = threading.Thread(target=run_flask)
flask_thread.start()

# Handle session state and query parameters
query_params = st.query_params
if st.session_state.zapier_response:
    variation_placeholder.text_area("Variation from Zapier", st.session_state.zapier_response, height=300)

# File uploader
uploaded_file = st.file_uploader("Upload an MP4 file", type=["mp4"])

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
        temp_file.write(uploaded_file.read())
        temp_filename = temp_file.name

    st.info("Transcribing audio...")
    result = model.transcribe(temp_filename)

    st.success("Transcription complete!")
    transcription_text = result["text"]
    st.text_area("Transcription", transcription_text, height=300)

    os.remove(temp_filename)

    if st.button("Create Variations"):
        st.info("Sending transcription to Zapier...")
        zapier_webhook_url = "https://hooks.zapier.com/hooks/catch/6652482/2z9cojg/"
        callback_url = "https://video-transcription-vertex.streamlit.app/webhook"

        response = requests.post(zapier_webhook_url, json={"transcription": transcription_text, "callback_url": callback_url})

        if response.status_code == 200:
            st.success("Transcription sent successfully! Waiting for Zapier to respond...")
        else:
            st.error(f"Failed to send transcription. Error: {response.status_code}")
