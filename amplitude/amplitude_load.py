import os
import zipfile
import gzip
import logging
import shutil
from datetime import datetime

# variables for directories 
log_dir = "load_logs" # load logs
data_dir = "data_zip_files" # same directory for where the amplitude zip data is dropped
unzipped_dir = "unzipped_data" # where the jsons go
archive_dir = os.path.join(data_dir, "archive") # where zips are moved after processing

# make the directories
os.makedirs(log_dir, exist_ok=True)
os.makedirs(data_dir, exist_ok=True)
os.makedirs(unzipped_dir, exist_ok=True)
os.makedirs(archive_dir, exist_ok=True)

# timestamp variable for the load logs
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

# setting up logging
log_filename = os.path.join(log_dir, f"amplitude_load_{timestamp}.log")
logging.basicConfig(
    filemode = "a",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=log_filename
)
logger = logging.getLogger()