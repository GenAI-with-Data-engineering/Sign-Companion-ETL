import os
from google.cloud import storage

# Set your Google Cloud Storage credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "orbital-outpost-401915-ff694c125d79.json"

# Replace these with your own values
bucket_name = "signlanguagevideos"
source_directory = "data/videos"

def upload_videos_to_gcs(bucket_name, source_directory):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    for root, _, files in os.walk(source_directory):
        for filename in files:
            local_file_path = os.path.join(root, filename)
            remote_blob_name = os.path.relpath(local_file_path, source_directory)

            # Upload the video file to GCS
            blob = bucket.blob(remote_blob_name)
            blob.upload_from_filename(local_file_path)

            print(f"Uploaded {local_file_path} to {bucket_name}/{remote_blob_name}")

if __name__ == "__main__":
    upload_videos_to_gcs(bucket_name, source_directory)
