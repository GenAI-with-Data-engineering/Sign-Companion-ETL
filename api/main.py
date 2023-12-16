
from fastapi import FastAPI, HTTPException
import pandas as pd
from typing import List, Optional
from pydantic import ValidationError, BaseModel
import boto3
import os
from dotenv import load_dotenv
import uuid
import re
import sqlite3
import whisper
import subprocess
from .I3D_Sign_Language_Classification.aslpipeline import router

model = whisper.load_model("base")


load_dotenv()
app = FastAPI()



class Transcript(BaseModel):
    transcript: str
    sign_language: Optional[str] = "ASL"

class Videos(BaseModel):
    video_list: List[int]
    sign_language: Optional[str] = "ASL"

videos = [
    {"name": "video1.mp4", "duration": 120},
    {"name": "video2.mp4", "duration": 180},
    {"name": "video3.mp4", "duration": 90},
]

s3 = boto3.client('s3',region_name='us-east-1',
                            aws_access_key_id = os.environ.get('AWS_ACCESS_KEY'),
                            aws_secret_access_key = os.environ.get('AWS_SECRET_KEY'))


@app.get("/videos")
async def get_videos():
    df = pd.read_csv('data/features_df.csv')
    return df.head().to_dict()

@app.get("/transcript")
async def create_transcript(filename:str):
    raw_input_dir = "data/audio_files/raw_input/"
    result = model.transcribe(raw_input_dir + filename)
    return {"transcript": result["text"]}

@app.post("/search_video_ids")
async def search_video_ids(transcript: Transcript):
    conn = sqlite3.connect('data/metadata.db')
    c = conn.cursor()

    try:
        words_only = re.sub(r'[^a-zA-Z\s]', '', transcript.transcript)
        words = words_only.split()

        video_ids = []
        for word in words:
            matching_rows = c.execute(f"SELECT video_id FROM {transcript.sign_language}_Table WHERE word=?", (word.lower(),)).fetchall()
            if matching_rows:
                for matching_row in matching_rows:
                    video_ids.append(int(matching_row[0]))
            else:
                letters = list(word.lower())
                print({"Letters": letters})
                for letter in letters:
                    matching_rows = c.execute(f"SELECT video_id FROM {transcript.sign_language}_Table WHERE word=?", (letter,)).fetchall()
                    for matching_row in matching_rows:
                        video_ids.append(int(matching_row[0]))
        print({"video_ids":video_ids})

        return {'video': [int(id) for id in video_ids]}
    except ValueError as e:
        return {"error": str(e)}
    finally:
        conn.close()






@app.post("/video_merge")
async def combine_videos(videos: Videos):
    final_video_bucket = 'signcompanion'
    local_save_path = 'data/audio_files/final_sign_video/'
    video_list = videos.video_list
    input_file_list = os.path.join('data/videos', 'input_list.txt')

    try:
        with open(input_file_list, 'w') as f:
            for video in video_list:
                file_path =f"{video}.mp4"
                f.write(f"file '{file_path}'\n")

        result_clip_name = str(uuid.uuid4()) + "_" + videos.sign_language + '.mp4'
        result_clip_path = os.path.join(local_save_path, result_clip_name)

        ffmpeg_command = (
            f"ffmpeg -f concat -safe 0 -i {input_file_list} -c copy {result_clip_path}"
        )

        subprocess.run(ffmpeg_command, shell=True, check=True)

        s3key = "final_sign_video/" + result_clip_name
        s3.upload_file(result_clip_path, final_video_bucket, s3key)

        return {"key_name": result_clip_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        os.remove(input_file_list)

app.include_router(router)