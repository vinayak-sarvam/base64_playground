import streamlit as st
import base64
import os
import json
import wave
from datetime import datetime
from pydub import AudioSegment

# Page configuration for better accessibility
st.set_page_config(
    page_title="Sarvam TTS Audio Converter",
    page_icon="🔊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better accessibility
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    .subheader {
        font-size: 1.5rem;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    .file-info {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .stButton button {
        width: 100%;
        height: 3rem;
        font-size: 1.2rem;
        font-weight: bold;
    }
    .download-button {
        margin-top: 10px;
    }
    .error-message {
        background-color: #ffebee;
        color: #c62828;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .success-message {
        background-color: #e8f5e9;
        color: #2e7d32;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    /* Improve focus indicators for keyboard navigation */
    *:focus {
        outline: 3px solid #4299e1 !important;
        outline-offset: 2px !important;
    }
</style>
""", unsafe_allow_html=True)

# Create output directory if it doesn't exist
if not os.path.exists('audio_files'):
    os.makedirs('audio_files')

def save_audio_tts_method(base64_string, filename):
    """Save base64 string as WAV file - exactly as in Sarvam TTS API response handling"""
    # Decode the base64-encoded audio data
    audio = base64.b64decode(base64_string)
    
    # Save the audio as a .wav file
    with wave.open(filename, "wb") as wav_file:
        # Set the parameters for the .wav file
        wav_file.setnchannels(1)  # Mono audio
        wav_file.setsampwidth(2)  # 2 bytes per sample
        wav_file.setframerate(22050)  # Sample rate of 22050 Hz

        # Write the audio data to the file
        wav_file.writeframes(audio)
    
    return filename

def convert_to_mp3(wav_file, mp3_file):
    """Convert WAV file to MP3 format"""
    sound = AudioSegment.from_wav(wav_file)
    sound.export(mp3_file, format="mp3")
    return mp3_file

def get_readable_file_size(size_in_bytes):
    """Convert bytes to human-readable file size"""
    for unit in ['B', 'KB', 'MB']:
        if size_in_bytes < 1024.0:
            return f"{size_in_bytes:.1f} {unit}"
        size_in_bytes /= 1024.0
    return f"{size_in_bytes:.1f} GB"

def main():
    # Main header with screen reader friendly markup
    st.markdown('<h1 class="main-header">Base64 Audio Converter</h1>', unsafe_allow_html=True)
    st.markdown("""
    <p aria-live="polite">
        Convert Sarvam TTS API base64 output to WAV or MP3 files. 
        This tool processes the JSON response from Sarvam's TTS API and extracts audio data.
    </p>
    """, unsafe_allow_html=True)
    
    # Sample input with single audio string matching Sarvam TTS API format
    sample_input = {
        "request_id": "sarvam_tts_request",
        "audios": ["UklGRiQMAABXQVZFZm10IBAAAAABAAEAIlYAAESsAAACABAAZGF0YQAMAAAxMjM="]
    }
    
    # Instructions with accessibility considerations
    st.markdown("""
    ### How to use:
    1. Call the Sarvam TTS API to generate speech
    2. Copy the JSON response containing the base64 audio string
    3. Paste it below and select your preferred output format
    4. Click the Convert button to generate playable audio file(s)
    5. Play the audio or download the file(s)
    """)
    
    # Input area for JSON with sample
    json_input = st.text_area(
        "Paste Sarvam TTS API response here", 
        json.dumps(sample_input, indent=2),
        height=200,
        help="Paste the JSON response from Sarvam's TTS API here. It should contain a 'request_id' and 'audios' array."
    )
    
    # Format selection with accessibility labels
    st.markdown('<p id="format-label">Select output format:</p>', unsafe_allow_html=True)
    output_format = st.radio(
        "Output format",
        ["WAV", "MP3", "Both"],
        horizontal=True,
        index=0,
        help="Choose the audio format you want to convert to. WAV is higher quality but larger file size."
    )
    
    # Conversion button with accessible label
    convert_button = st.button(
        "Convert Audio",
        help="Click to convert the base64 string to audio file(s)"
    )
    
    if convert_button:
        try:
            # Parse JSON
            data = json.loads(json_input)
            
            # Basic validation
            if 'audios' not in data or not isinstance(data['audios'], list) or not data['audios']:
                st.markdown('<div class="error-message" role="alert">Invalid JSON format. Must contain "audios" array with at least one entry.</div>', unsafe_allow_html=True)
                return
            
            # Get the single audio string
            audio_string = data['audios'][0]
            
            # Generate filename with timestamp and request_id
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            request_id = data.get('request_id', 'audio').replace('/', '_')
            base_filename = f"{timestamp}_{request_id}"
            wav_filename = f"audio_files/{base_filename}.wav"
            
            # Processing notification for screen readers
            st.markdown('<div aria-live="assertive">Processing your audio file...</div>', unsafe_allow_html=True)
            
            # Always save WAV first (even if only MP3 is requested, we need WAV to create MP3)
            wav_file = save_audio_tts_method(audio_string, wav_filename)
            
            # Success message for screen readers
            st.markdown('<div class="success-message" role="status">Audio conversion successful! You can now play or download your file(s).</div>', unsafe_allow_html=True)
            
            # Create two columns for displaying files
            col1, col2 = st.columns(2)
            
            # First column: WAV file (if WAV or Both is selected)
            if output_format in ["WAV", "Both"]:
                with col1:
                    st.markdown('<h2 class="subheader">WAV File</h2>', unsafe_allow_html=True)
                    
                    # Display WAV audio player with accessibility attributes
                    st.markdown('<label for="wav-player">Play WAV audio:</label>', unsafe_allow_html=True)
                    with open(wav_file, "rb") as f:
                        wav_bytes = f.read()
                        st.audio(wav_bytes, format='audio/wav')
                    
                    # Download button for WAV with accessible label
                    with open(wav_file, "rb") as file:
                        st.download_button(
                            label="📥 Download WAV File",
                            data=file,
                            file_name=os.path.basename(wav_file),
                            mime="audio/wav",
                            help="Download the generated WAV file to your device"
                        )
            
            # Second column or first if only MP3 is selected: MP3 file
            if output_format in ["MP3", "Both"]:
                with col2 if output_format == "Both" else col1:
                    st.markdown('<h2 class="subheader">MP3 File</h2>', unsafe_allow_html=True)
                    
                    # Convert to MP3
                    mp3_filename = f"audio_files/{base_filename}.mp3"
                    mp3_file = convert_to_mp3(wav_file, mp3_filename)
                    
                    # Display MP3 audio player with accessibility attributes
                    st.markdown('<label for="mp3-player">Play MP3 audio:</label>', unsafe_allow_html=True)
                    with open(mp3_file, "rb") as f:
                        mp3_bytes = f.read()
                        st.audio(mp3_bytes, format='audio/mp3')
                    
                    # Download button for MP3 with accessible label
                    with open(mp3_file, "rb") as file:
                        st.download_button(
                            label="📥 Download MP3 File",
                            data=file,
                            file_name=os.path.basename(mp3_file),
                            mime="audio/mp3",
                            key="mp3_download",
                            help="Download the generated MP3 file to your device"
                        )
                
            # If only MP3 is selected, we can remove the WAV file to save space
            if output_format == "MP3" and os.path.exists(wav_file):
                try:
                    os.remove(wav_file)
                except:
                    pass
                
        except json.JSONDecodeError:
            st.markdown('<div class="error-message" role="alert">Invalid JSON format. Please check your input and ensure it is properly formatted.</div>', unsafe_allow_html=True)
        except Exception as e:
            st.markdown(f'<div class="error-message" role="alert">Error: {str(e)}</div>', unsafe_allow_html=True)
            
    # Add hint about expected JSON structure with semantic markup
    st.markdown("""
    <div aria-labelledby="json-format-header">
        <h3 id="json-format-header">Expected Sarvam TTS API Response Format:</h3>
        <pre aria-label="JSON example format">
{
    "request_id": "unique_identifier",
    "audios": [
        "base64_encoded_audio_data"
    ]
}
        </pre>
    </div>
    """, unsafe_allow_html=True)
    
    # Add information about the Sarvam TTS API with the specific endpoint URL
    st.markdown("""
    ### About Sarvam TTS API
    
    The Sarvam Text-to-Speech (TTS) API converts text into spoken audio. The output is a wave file encoded as a base64 string.
    This converter tool helps you transform that base64-encoded audio into playable WAV or MP3 files that you can use in your applications.
    
    For more information, visit the [Sarvam TTS API documentation](https://docs.sarvam.ai/api-reference-docs/endpoints/text-to-speech).
    """)

if __name__ == '__main__':
    main()
