import os
from kaggle.api.kaggle_api_extended import KaggleApi

api = KaggleApi()
api.authenticate()

# Specify the dataset you want to download
dataset_name = 'risangbaskoro/wlasl-processed'

# Specify the directory where you want to download the dataset
download_dir = 'projects/fall2023/genaicourse/Sign-Companion-ETL/data'

# Download the dataset
api.dataset_download_files(dataset_name, path=download_dir, unzip=True)

print(f"Dataset {dataset_name} downloaded to {download_dir}")
