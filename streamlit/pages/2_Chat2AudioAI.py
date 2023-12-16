import streamlit as st
import os
import openai
import boto3
import requests
from dotenv import load_dotenv
load_dotenv()

# Set your OpenAI GPT API key
openai.api_key = os.environ.get('OPENAI_SECRET_KEY')
signcompanion_bucket = os.environ.get('SIGNCOMPANION_BUCKET')
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_KEY')


s3 = boto3.client('s3',region_name='us-east-1',
                        aws_access_key_id = AWS_ACCESS_KEY_ID,
                        aws_secret_access_key = AWS_SECRET_ACCESS_KEY)

def generate_prompt_response(transcript:str, user_input):

    final_prompt = f"The following is a transcript of an audio file \n{transcript} \n Now answer the following question: \n What did the explorer find in the old book??. \n Response:"
    response = openai.Completion.create(
        engine="text-davinci-002",  
        prompt=final_prompt,
        max_tokens=100,  
        temperature=0.7, 
    )

    return response.choices[0].text.strip()


def list_files_from_s3():
    audio_files=[]
    response = s3.list_objects_v2(Bucket=signcompanion_bucket, Prefix="raw_input/")
    files = response.get("Contents")
    for file in files:
        audio_files.append(file['Key'])
    return audio_files

def main():
    st.title("Audio File Selector")
    
    audio_files = list_files_from_s3()

    selected_audio = st.selectbox("Select an Audio File", audio_files)
    print(selected_audio)
    audio_file_name = selected_audio.split('/')[1]
    if os.path.exists(audio_file_name):
        st.audio(f"data/audio_files/raw_input/{audio_file_name}")


    transcript_key = f"transcripts/{audio_file_name.split('.')[0]}"
    transcript_obj = s3.get_object(Bucket=signcompanion_bucket, Key=transcript_key)
    transcript_content = transcript_obj['Body'].read().decode('utf-8')
    st.text("Transcript:")
    st.text(transcript_content)

    user_input = st.file_uploader("**Upload a sign language video file:**",
                                     type=["mp4", "avi", "mov"],
                                     label_visibility='collapsed')
    
    if st.button("Generate Response"):
        if user_input:
            response = generate_prompt_response(transcript_content,user_input)

            st.write("Generated Response:")
            st.write(response)
        else:
            st.warning("Please enter a prompt.")

if __name__ == "__main__":
    main()