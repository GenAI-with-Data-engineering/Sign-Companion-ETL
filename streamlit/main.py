import streamlit as st
import whisper

st.title("SignIt:wind_blowing_face::ok_hand:")
st.header("Upload an audio file or Paste a youtube link")
    
col1, col2 = st.columns(2)

with col1:
    source = st.radio("Select Model card", ("OpenAI Whisper API", "Google Speech to text API"))
    uploaded_file = st.file_uploader("Upload an audio file (mp3, mp4, m4a)", type=["mp3", "mp4", "m4a"])

    #Upload File section (SignIt - Part 1)
    if source == "OpenAI Whisper API":

        if (uploaded_file):
            model = whisper.load_model("base")
            result = model.transcribe("data/Recording (2).m4a")
            st.write(result["text"])

        else:
            st.warning("Please upload a file and select the language to translate to")

    elif source == "Google Speech to text API":
        st.write("In progress")



