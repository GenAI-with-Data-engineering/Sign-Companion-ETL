from snowflake.snowpark import Session
import os
import csv

def file_exists_locally(file_path):
    return os.path.exists(file_path)

def get_video_duration(video_path):
    try:
        from moviepy.editor import VideoFileClip
        clip = VideoFileClip(video_path)
        return clip.duration
    except UnicodeDecodeError as e:
        print(f"Error reading video {video_path}: {e}")
        return None

def create_session_object():
   connection_parameters = {
      "account": "CXYGUVM-MTB44847",
      "user": "genai",
      "password": "damg7374*",
      "role": "TRANSFORMER",
      "warehouse": "TRANSFORMER_WAREHOUSE",
      "database": "SIGNMETADATA",
      "schema": "SIGNMETADATA_FINAL"
   }
   session = Session.builder.configs(connection_parameters).create()
   print(session.sql('select current_warehouse(), current_database(), current_schema()').collect())
   return session

currSession = create_session_object()
print(currSession)

df_metadata = currSession.sql('select * from test').to_pandas()

currSession.close()

local_video_dir = 'data/videos'
schema_file_name = "schema.csv"
failure_count = 0 

# Generate the schema file
with open(schema_file_name, 'w', newline='') as schema_file:
    writer = csv.writer(schema_file)
    writer.writerow(["VIDEO_URI", "TIME_SEGMENT_START", "TIME_SEGMENT_END", "LABEL", "ANNOTATION_FRAME_TIMESTAMP"])

    for _, row in df_metadata.iterrows():
        video_id = row['video_id']
        label = row['word']
        video_file_path = os.path.join(local_video_dir, f"{video_id}.mp4")

        if file_exists_locally(video_file_path):
            video_uri = f"gs://signcompanion-videos/{video_id}.mp4"
            video_duration = get_video_duration(video_file_path)
            if video_duration is not None:
                time_segment_start = 0
                time_segment_end = video_duration
                annotation_frame_timestamp = video_duration / 2
                writer.writerow([video_uri, time_segment_start, time_segment_end, label, annotation_frame_timestamp])
            else:
                failure_count += 1
        else:
            print(f"Video file {video_id}.mp4 does not exist in the local directory '{local_video_dir}'.")
            failure_count += 1

print(f"Schema file '{schema_file_name}' has been generated with time segment and annotation frame timestamps.")
print(f"Failed to read video files for {failure_count} videos.")
