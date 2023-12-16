
#-------------------------------------------------------------------------------------------------------------------------------
#Fundamental template
import streamlit as st
import os
import requests
from dotenv import load_dotenv
import boto3
import sqlite3
import yt_dlp
import time

load_dotenv()

#-------------------------------------------------------------------------------------------------------------------------------
#Setting up Variables
signcompanion_bucket = os.environ.get('SIGNCOMPANION_BUCKET')
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_KEY')
UPLOAD_DIR = "data/audio_files/raw_input"
if not os.path.exists(UPLOAD_DIR):
            os.makedirs(UPLOAD_DIR)
AIRFLOW_URL = os.environ.get("AIRFLOW_URL")
AIRFLOW_USERNAME = os.environ.get('AIRFLOW_USERNAME')
AIRFLOW_PASSWORD = os.environ.get('AIRFLOW_PASSWORD')
dag_id = 'sign_conversion'
task_id = 'merge_videos'
s3client = boto3.client('s3',region_name='us-east-1',
                        aws_access_key_id = AWS_ACCESS_KEY_ID,
                        aws_secret_access_key = AWS_SECRET_ACCESS_KEY)

ALLOWED_SIGN_LANGUAGES = ["ASL"]

#-------------------------------------------------------------------------------------------------------------------------------
#Setting up functions

def triggerDAG(filename:str):
    url = f"{AIRFLOW_URL}/api/v1/dags/{dag_id}/dagRuns"
    auth = (AIRFLOW_USERNAME, AIRFLOW_PASSWORD)
    headers = {"Content-Type": "application/json"}
    data = {"conf": {"filename": filename}}
    print(url)
    response = requests.post(url, headers=headers, json=data, auth=auth)
    
    return response.status_code

def check_status_task():
    try:

        auth = (AIRFLOW_USERNAME, AIRFLOW_PASSWORD)
        requests.get(url=f'{AIRFLOW_URL}/dags/{dag_id}/dagRuns',auth=auth)
        dag_run_id = response.json()["dag_runs"][0]['dag_run_id']

        response = requests.get(url=f'{AIRFLOW_URL}/dags/{dag_id}/dagRuns/{dag_run_id}/taskInstances/{task_id}',auth=auth)
        task_status = response.json()['state']
    except:
        task_status = "Faied to get status"
    return task_status

if "button_clicked" not in st.session_state:    
    st.session_state.button_clicked = False

def callback():
    st.session_state.button_clicked = True

    
def download_yt_video(video_url,filename):
    ydl_opts = {
        'format': 'm4a/bestaudio/best',
        'outtmpl': f"{UPLOAD_DIR}/{filename}.%(ext)s",
        'postprocessors': [{ 
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'm4a' ,
                }]
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        error_code = ydl.download(video_url)

#------------------------------------------------------------------------------------------------------------------

def main():

    st.title("Sign Companion")
    st.header("Upload an audio file or Paste a youtube link")
    

    source = st.radio("Select audio source", ("Upload file", "Enter Youtube link"))

    #Upload File section (SignIt - Part 1)
    if source == "Upload file":

        uploaded_file = st.file_uploader("Upload an audio file (mp3, mp4, m4a)", type=["mp3", "mp4", "m4a"])
        sign_language = st.selectbox("Select the sign language to translate to",options=ALLOWED_SIGN_LANGUAGES)
        upload = st.button('Upload file',on_click=callback)

        if (upload and sign_language):
            #Adding sign language(ASL/ISL/BSL) to the end of file name
            file_name = uploaded_file.name.split(".")[0] + "_"+ sign_language + "." +uploaded_file.name.split(".")[1]
            s3_key = f'raw_input/{file_name}'

            with open(os.path.join(UPLOAD_DIR, file_name), "wb") as f:
                f.write(uploaded_file.read())

            st.success("File Uploaded successfully!")
            
            st.audio(uploaded_file)
            
            file_contents = uploaded_file.read()
            s3client.put_object(Bucket=signcompanion_bucket, Key=s3_key, Body=file_contents)
            status = triggerDAG(file_name)
            if status == 200:
                st.write("DAG Triggered")
            else:
                st.warning("DAG failed to trigger")

            

        else:
            st.warning("Please upload a file and select the language to translate to")

    elif source == "Enter Youtube link":
        youtube_link = st.text_input('Paste the youtube link here', 'www.youtube.com/xxx')
        file_name = st.text_input('Enter a file name for the link','Default')

        sign_language = st.selectbox("Select the sign language to translate to",options=ALLOWED_SIGN_LANGUAGES)
        upload = st.button('Upload file')
        if upload and sign_language:

            if file_name:
                file_name = file_name + "_"+ sign_language
                local_file_path = UPLOAD_DIR + "/" +file_name
                download_yt_video(youtube_link,file_name)
                st.write(f"Audio saved at {UPLOAD_DIR}")
                
                # Upload the audio file to S3
                s3_prefix = "raw_input/"
                s3_file_key = s3_prefix + file_name + ".m4a"
                with open(f"{local_file_path}.m4a", 'rb') as f:
                    s3client.put_object(Bucket=signcompanion_bucket, Key=s3_file_key, Body=f)                
                st.write(f"File uploaded to S3 bucket {signcompanion_bucket} with key {s3_file_key}")
                status = triggerDAG(f"{file_name}.m4a")
                if status == 200:
                    st.write("DAG Triggered")
            else:
                st.error("Please enter a file name to save the audio.")



    
    st.header("Converted Sign Language Video")
    
    video_directory = "data/audio_files/final_sign_video"
    file_names = [file for file in os.listdir(video_directory) if file.endswith(('.mp4', '.avi', '.mkv'))]

    option = st.selectbox('Select from available videos', options=file_names)

    if option:
        video_path = os.path.join(video_directory, option)
        st.video(video_path)

if __name__ == "__main__":
    main()
 
