
from snowflake.snowpark import Session
import pandas as pd
from snowflake.snowpark.dataframe import DataFrame

import csv




def create_session_object():
   connection_parameters = {
 
     "account": "",
      "user": "",
      "password": "*",
      "role": "",
      "warehouse": "",
      "database": "",
      "schema": ""
   }
   session = Session.builder.configs(connection_parameters).create()
   print(session.sql('select current_warehouse(), current_database(), current_schema()').collect())
   return session

currSession = create_session_object()
print(currSession)
df_metadata = currSession.sql('select * from test').to_pandas()


currSession.close()

schema_file_name = "schema.csv"
with open(schema_file_name, 'w', newline='') as schema_file:
   writer = csv.writer(schema_file)
   writer.writerow(["VIDEO_URI", "TIME_SEGMENT_START", "TIME_SEGMENT_END", "LABEL", "ANNOTATION_FRAME_TIMESTAMP"])

   for _, row in df_metadata.iterrows():
      video_id = row['video_id']
      label = row['word']
      video_uri = f"gs://folder/{video_id}.mp4"
      writer.writerow([video_uri, 0, "inf", label, ""])

print(f"Schema file '{schema_file_name}' has been generated for all video IDs with labels from the Snowflake table.")



