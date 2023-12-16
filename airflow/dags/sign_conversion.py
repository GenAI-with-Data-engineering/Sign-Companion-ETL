import boto3
from airflow import DAG
from airflow.decorators import dag
from airflow.operators.dummy import DummyOperator
from airflow.operators.python_operator import PythonOperator,BranchPythonOperator
from airflow.models import Variable
from airflow.utils.trigger_rule import TriggerRule

from datetime import datetime,timedelta
import requests
import json

import sqlite3
import os
import pytz

#-------------------------------------------------------------------------------------------------------------------
#                                Setting up variable
#--------------------------------------------------------------------------------------------------------------------
# Set up AWS credentials
aws_access_key_id = os.environ.get('AWS_ACCESS_KEY')
aws_secret_access_key = os.environ.get('AWS_SECRET_KEY')
signcompanion_bucket = os.environ.get('SIGNCOMPANION_BUCKET')
token = os.environ.get('OPENAI_SECRET_KEY')
API_URL= os.environ.get('API_URL')
user_input = {
        "filename": "Recording_ASL.mp3"
        }

# Set up AWS clients
s3_client = boto3.client('s3',
                         aws_access_key_id=aws_access_key_id,
                         aws_secret_access_key=aws_secret_access_key)


#-------------------------------------------------------------------------------------------------------------------
#                                Setting up functions
#--------------------------------------------------------------------------------------------------------------------


# Define function for Task 1
def create_transcript(**kwargs):

    filename = kwargs['dag_run'].conf['filename']
    url = f"{API_URL}/transcript"

    response = requests.get(url, params={"filename": filename})
    transcript = response.json() 
    if response.status_code == 200:
        return transcript["transcript"]


# Define function for Task 2
def write_to_s3(transcript,**kwargs):
    # Write the file to processed transcript folder in signcompanion bucket
    fileToWrite = kwargs['dag_run'].conf['filename']
    result = "transcripts/"+fileToWrite.split('.')[0]
    s3_client.put_object(Body=transcript.encode(), Bucket=signcompanion_bucket, Key=result)

# Define function for Task 3
def video_ids(transcript,**kwargs):
    sign_language = kwargs['dag_run'].conf['filename'].split(".")[0].split("_")[1]
    url = f"{API_URL}/search_video_ids"

    response = requests.post(url,json={"transcript": transcript, "sign_language":sign_language})
    if response.status_code == 200:
        video_list = json.loads(response.text)
        return video_list['video']
    else:
        return []
    
# Define function for Task 4
def merge_videos(video_list,**kwargs):
    url = f"{API_URL}/video_merge"
    sign_language = kwargs['dag_run'].conf['filename'].split(".")[0].split("_")[1]
    video_list_json = json.loads(video_list)
    print({"video_list_json":video_list_json})
    response = requests.post(url,json={"video_list": video_list_json, "sign_language":sign_language})
    if response.status_code == 200:
        res = json.loads(response.text)
        return res['key_name']
    else:
        return {'video': []}



# Define the DAG
dag = DAG('sign_conversion', description='DAG for processing audio files and converting them to sign language',
          schedule_interval='@once',  
          start_date=datetime(2023, 12, 13),
          params=user_input,
          catchup=True,  
          dagrun_timeout=timedelta(hours=2), 
          )
# Define the tasks
task1 = PythonOperator(task_id='create_transcript', python_callable=create_transcript, dag=dag)
task2 = PythonOperator(task_id='write_to_s3', python_callable=write_to_s3, dag=dag, op_kwargs={'transcript': "{{ ti.xcom_pull(task_ids='create_transcript') }}"})
task3 = PythonOperator(task_id='video_ids', python_callable=video_ids, dag=dag, op_kwargs={'transcript': "{{ ti.xcom_pull(task_ids='create_transcript') }}"})
task4 = PythonOperator(task_id='merge_videos', python_callable=merge_videos, dag=dag, op_kwargs={'video_list': "{{ ti.xcom_pull(task_ids='video_ids') }}"})
complete = DummyOperator(task_id="complete", trigger_rule=TriggerRule.NONE_FAILED,dag=dag)

# Define the task dependencies
task1 >> task2 >> task3 >> task4 >> complete
