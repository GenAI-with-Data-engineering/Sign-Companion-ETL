import streamlit as st
import requests
import os

API_URL= "http://localhost:8000/classify"

st.title("Sign Language Recognition App")

def upload_video():
    st.write("Upload a sign language video file.")
    uploaded_file = st.file_uploader("Choose a video file", type=["mp4", "avi"])

    if uploaded_file is not None:
        save_directory = "ml-model/I3D_Sign_Language_Classification/videos"
        os.makedirs(save_directory, exist_ok=True)

        video_path = os.path.join(save_directory, uploaded_file.name)
        with open(video_path, "wb") as f:
            f.write(uploaded_file.read())

        st.write(f"Video file '{uploaded_file.name}' uploaded successfully.")
        return uploaded_file.name

def call_fastapi_endpoint(filename, dataset="WLASL2000"):
    st.write("Calling FastAPI endpoint...")

    params = {"video": f"videos/{filename}",
             "dataset": dataset}
    

    response = requests.get(API_URL, params=params)

    if response.status_code == 200:
        predictions = response.json()
        st.write("Top 5 Predictions:")
        for label, confidence in predictions.items():
            st.write(f"{label}: {confidence:.2%}")
    else:
        st.error(f"Error: {response.status_code} - {response.text}")

filename = upload_video()

if filename:
    st.write("Video uploaded successfully.")
    dataset = st.selectbox("Select Dataset", ["WLASL100", "WLASL2000"])
    classify_button = st.button("Classify Sign Language")

    if classify_button:
        call_fastapi_endpoint(filename, dataset)
