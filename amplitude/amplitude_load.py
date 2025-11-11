import os
import boto3
import logging
from dotenv import load_dotenv
from datetime import datetime

# load environment for our load aws access key, secret key, and bucket name
load_dotenv()

# referencing variables from the .load_env file
aws_access_key = os.getenv("AWS_ACCESS_KEY")
aws_secret_key = os.getenv("AWS_SECRET_KEY")
bucket_name = os.getenv("AWS_BUCKET")

# the directory that contains all of the processed json files
unzipped_dir = 'unzipped_data'

# directory variables
logs_dir = "s3_upload_logs"
archive_dir = "archived_json_data"

# making directories
os.makedirs(logs_dir, exist_ok = True)
os.makedirs(archive_dir, exist_ok = True)

# timestamp variable
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

# log configuration
log_filename = os.path.join(logs_dir, f"amplitude_s3_upload_{timestamp}.log")
logging.basicConfig(
    filemode = "a",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=log_filename
)
logger = logging.getLogger()

# Create an S3 Client using AWS Credentials
s3_client = boto3.client(
    's3',
    aws_access_key_id = aws_access_key,
    aws_secret_access_key = aws_secret_key
)

# go through my unzipped_data directory and look for any .json files
files_to_upload = []
try:
    all_data_files = os.listdir(unzipped_dir)
    for f in all_data_files:
        if f.endswith(".json"):
            files_to_upload.append(f)
except Exception as e:
    logger.error(f"Could not read {unzipped_dir} directory: {e}")

if not files_to_upload:
    logger.info("No new .json files to upload")
else:
    if len(files_to_upload) == 1:
        logger.info("There is 1 json file to upload")
    else:
        logger.info(f"There are {len(files_to_upload)} json files to upload")
    
    for filename in files_to_upload: # go through any new .json files
        local_file_path = os.path.join(unzipped_dir, filename) # full local file path to be read
        archive_file_path = os.path.join(archive_dir, filename) # archive file path

        # s3filename = f"raw_data/amplitude/{filename}"
        aws_file_destination = "python-import/" + filename

        try:
            s3_client.upload_file(
                local_file_path
                , bucket_name
                , aws_file_destination
            )
            logger.info(f"Uploaded {local_file_path} to s3://{bucket_name}/{aws_file_destination}")

            os.rename(local_file_path, archive_file_path)
            logger.info(f"Archived {local_file_path}, to {archive_file_path}")

        except Exception as e:
            logger.error(f"Failed during upload/archive for {local_file_path}: {e}")

    logger.info("s3 upload finished.")

            