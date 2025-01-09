import streamlit as st
import whisper
import tempfile
import os
import requests  # Required for sending POST requests

# Set up Streamlit app
st.title("Step 1: Upload The Video You Want To Convert")

# Load Whisper model
@st.cache_resource
def load_model():
    return whisper.load_model("base")  # Use other models like 'tiny', 'large' as needed

model = load_model()

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
        
        # Send the POST request with the transcription text
        response = requests.post(zapier_webhook_url, json={"transcription": transcription_text})

        if response.status_code == 200:
            st.success("Transcription sent successfully!")
        else:
            st.error(f"Failed to send transcription. Error: {response.status_code}")
