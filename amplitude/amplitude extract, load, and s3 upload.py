import requests
import os
import zipfile
import gzip
import logging
import shutil
import tempfile
import boto3
from dotenv import load_dotenv
from datetime import datetime, timedelta

# making a directory for the logs
log_dir = "extract_logs"
log_dir = "load_logs" # load logs
data_dir = "data_zip_files" # same directory for where the amplitude zip data is dropped
unzipped_dir = "unzipped_data" # where the jsons go
archive_dir = "archive" # where zips are moved after processing
logs_dir = "s3_upload_logs" 

os.makedirs(log_dir, exist_ok=True)
os.makedirs(log_dir, exist_ok=True)
os.makedirs(data_dir, exist_ok=True)
os.makedirs(unzipped_dir, exist_ok=True)
os.makedirs(archive_dir, exist_ok=True)
os.makedirs(logs_dir, exist_ok = True)


