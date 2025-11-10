import os
import zipfile
import gzip
import logging
import shutil
import tempfile
from datetime import datetime

# variables for directories 
log_dir = "load_logs" # load logs
data_dir = "data_zip_files" # same directory for where the amplitude zip data is dropped
unzipped_dir = "unzipped_data" # where the jsons go
archive_dir = "archive" # where zips are moved after processing

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

print("Starting amplitude data processing...")

# finding all zip files in my data_zip_files directory
amplitude_zip_process_files = [] # starting an empty list for the loop append
try:
    all_data_zip_files = os.listdir(data_dir)
    for f in all_data_zip_files:
        if f.endswith(".zip") and os.path.isfile(os.path.join(data_dir, f)): # check if it ends in a zip file and IT is a file
            amplitude_zip_process_files.append(f) # then add it to the empty list
except Exception as e:
    logger.error(f"Could not read data directory {data_dir}: {e}")

if not amplitude_zip_process_files:
    logger.info("No new .zip files found to process.")
else:
    if len(amplitude_zip_process_files) == 1:
        logger.info("There is 1 file to process")
    else:
        logger.info(f"There are {len(amplitude_zip_process_files)} files to process")

# looping through each data zip file and processing it
for data_zip_name in amplitude_zip_process_files:
    data_zip_path = os.path.join(data_dir, data_zip_name)
    logger.info(f"Processing {data_zip_name}...")

    temp_dir = tempfile.mkdtemp()
    logger.info(f"Created temp directory: {temp_dir}")

    try: # extracting the data zip file into the temp directory
        with zipfile.ZipFile(data_zip_path, "r") as zip_ref:
            zip_ref.extractall(temp_dir)
            logger.info(f"{data_zip_name} extracted to {temp_dir}")

        numeric_folder_name = None

        for file in os.listdir(temp_dir):
            file_path = os.path.join(temp_dir, file)
            if os.path.isdir(file_path):
                numeric_folder_name = file
                break
        
        if numeric_folder_name is None:
            logger.error(f"No data sub-folder found inside {data_zip_name}. Temp dir: {temp_dir}")
            raise FileNotFoundError(f"No data sub-folder found inside {temp_dir}")
        
        numeric_folder_path = os.path.join(temp_dir, numeric_folder_name)
        logger.info(f"Found numeric data folder: {numeric_folder_name}")

        # go through the numeric folder and find all .gz files
        for root, _, files in os.walk(numeric_folder_path):
            for file in files:
                if file.endswith(".gz"):
                    gz_path = os.path.join(root, file)

                    zip_base_name = data_zip_name.replace('amplitude_data_', '').replace('.zip', '')
                    json_base_name = file.replace('.gz', '')

                    final_json_name = f"{zip_base_name}_{json_base_name}"
                    final_json_path = os.path.join(unzipped_dir, final_json_name)

                    logger.info(f"Decompressing {file} to {final_json_path}")

                    with gzip.open(gz_path, 'rb') as gz_file:
                        with open(final_json_path, 'wb') as out_file:
                            shutil.copyfileobj(gz_file, out_file)

        # move processed zip file to archive
        shutil.move(data_zip_path, os.path.join(archive_dir, data_zip_name))
        logger.info(f"Successfully processed and archived {data_zip_name}")

    except Exception as e:
        logger.info(f"An error occured processing {data_zip_name}: {e}. Leaving {data_zip_name} in place")
    
    # clean up temp directory
    finally:
        try:
            shutil.rmtree(temp_dir)
            logger.info(f"Deleted temp directory: {temp_dir}")
        except Exception as e:
            logger.info(f"Failed to delete temp directory {temp_dir}: {e}")

logger.info("Processing script is finished")
print("Processing script is finished")

        
