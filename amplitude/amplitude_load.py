import os
import zipfile
import gzip
import logging
import shutil
from datetime import datetime

# variables for directories 
log_dir = "load_logs" # load logs
data_dir = "data_zip_files" # directory for where the amplitude zip data is dropped
unzipped_dir = "unzipped_data" # where the jsons go
archive_dir = os.path.join(data_dir, "archive") # 

# make the directories
os.makedirs(log_dir, exist_ok=True)
os.makedirs(data_dir, exist_ok=True)
os.makedirs(unzipped_dir, exist_ok=True)
os.makedirs(archive_dir, exist_ok=True)


