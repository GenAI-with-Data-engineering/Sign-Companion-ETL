import os
import sqlite3

# Connect to the SQLite database
db_path = 'data/metadata.db'  # Replace with your actual database file path
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Retrieve video_ids from the database
cursor.execute("SELECT video_id FROM ASL_Table")
video_ids_from_db = [row[0] for row in cursor.fetchall()]

# Close the database connection
conn.close()

# Directory path where video files are stored
video_directory = 'data/videos/'

# Get the list of video files
video_files = [f for f in os.listdir(video_directory) if f.endswith('.mp4')]

# Identify video files to delete
videos_to_delete = [video_file for video_file in video_files if video_file[:-4] not in video_ids_from_db]

# Delete video files
for video_file in videos_to_delete:
    video_path = os.path.join(video_directory, video_file)
    os.remove(video_path)
    print(f"Deleted: {video_path}")

print("Deletion complete.")
