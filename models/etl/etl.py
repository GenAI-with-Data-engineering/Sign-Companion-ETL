import snowflake.connector
import json
import pandas as pd
from snowflake.connector.pandas_tools import write_pandas

def snowflake_connect():
    conn = snowflake.connector.connect(
        account = 'NNB96911.US-EAST-1',
        user = 'SHREYANGIPR25',
        database = 'SIGNMETADATA',
        schema = 'SIGNMETADATA_FINAL',
        password = 'Khushipr250103*',
        warehouse = 'TRANSFORMER_WAREHOUSE',
        role = 'TRANSFORMER',
    )
    return conn

## Create snowflake compatible schema from the downloaded data. This will create a 
## a table if it does not already exist.

def create_snowflake_table_schema(table_name,df):
    table_name = 'test'
    df_schema = pd.io.sql.get_schema(df, table_name)
    df_schema = str(df_schema).replace('TEXT', 'VARCHAR(16777216)')
    df_schema = str(df_schema).replace('CREATE TABLE', 'CREATE TABLE IF NOT EXISTS')
    cur = conn.cursor()
    return cur.execute(df_schema)

def write_to_snowflake_table(table_name,df):
    chunk_size = int(df.shape[0]/15000)+1
    start = 0
    for i in range(chunk_size):
        end = start + 15000
        temp_data = df.iloc[start:end]
        start = end
        success, num_chunks, num_rows, output = write_pandas(
                conn=conn,
                df=temp_data,
                table_name=table_name,
                database='SIGNMETADATA',
                schema='SIGNMETADATA_FINAL'
            )
        print("Inserted data from {0}".format(temp_data.index))
        print("{0},{1},{2},{3}".format(success,num_chunks, num_rows, output))
    return

# Chande read location S3 bucket
metadata = json.load(open(r'WLASL_v0.3.json'))

video_ids = []
words = []

for item in metadata:
    word = item['gloss']
    instances = item['instances']
    for instance in instances:
        video_id = instance['video_id']
        words.append(word)
        video_ids.append(video_id)

df = pd.DataFrame({'video_id': video_ids, 'word': words})

# print(df)

