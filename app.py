import streamlit as st
import whisper
import tempfile
import os

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
    st.text_area("Transcription", result["text"], height=300)

    # Clean up temporary file
    os.remove(temp_filename)
