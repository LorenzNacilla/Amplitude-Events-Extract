# Overview

This repo looks into extracting events data from the Amplitude API. There were two methods in calling the API - one using airbyte to call the API itself and then landing it in an azure blob storage, and the other with a python script. This repo mainly contains the python script to call the API but the method with airbyte and azure blob storage is used.

- [Overview](#overview)
- [➡️ General Data Flow](#️-general-data-flow)
- [Requirements](#requirements)
- [1. Extraction and Unzipping](#1-extraction-and-unzipping)
  - [Extraction](#extraction)
  - [JSON Unzipping](#json-unzipping)
- [2. Load](#2-load)
  - [AWS s3 Bucket Set-up](#aws-s3-bucket-set-up)
  - [Snowflake Storage Integration and Staging](#snowflake-storage-integration-and-staging)
  - [Python Load into s3](#python-load-into-s3)
- [3. Transform](#3-transform)

# ➡️ General Data Flow

![General Flow](https://github.com/LorenzNacilla/Amplitude-Events-Extract/blob/main/images/General%20Flow.png)
This is a general flow of the project. For the time being this is looking at more of the API call and the storing it into a bucket which is more for the airbyte flow shown below.

![Airbyte Flow](https://github.com/LorenzNacilla/Amplitude-Events-Extract/blob/main/images/Airbyte%20Flow.png)
This is a diagram that highlights the method of using airbyte and azure blob storage. A big pro of airbyte is that it is no-code and makes use of a UI. The use of airbyte

![Python Flow](https://github.com/LorenzNacilla/Amplitude-Events-Extract/blob/main/images/Python%20Flow.png)
This diagram shows the data flow when using python. A key part of when calling the API is that it will return a zip folder. Within that zip folder is a folder that contains several folders each containing one json file which is one hour of data depending on how many days is called from the API. The python scripts were written to extract the json data files from these folders.

# Requirements

Some packages that were installed:

- dotenv
- requests

To run the respective python scripts for extracting the data zip folder from the API, unzipping the folder and then uploading it to an s3 bucket - run the following command:

```python
pip install -r requirements.txt
```

# 1. Extraction and Unzipping

The `amplitude_extract.py` script is used to get the raw data from the API in the form of a zip data folder with each folder inside the zip folder containing a json file for one hour of a day.

The `amplitude_zip_process.py` script then unzips that data zip folder and extracts all of the json files from it.

## Extraction

The following script was used to extract the data zip folder from the API:

```python
import requests
import os
import logging
from dotenv import load_dotenv
from datetime import datetime, timedelta

# making a directory for the logs
log_dir = "extract_logs"
os.makedirs(log_dir, exist_ok=True)

# log filename for when the script is run
log_filename = os.path.join(log_dir, f"amplitude_extract_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

# configuration of the logs
logging.basicConfig(
    filemode = "a", # append the data when script is run and not overwrite
    level=logging.INFO, # record any message that is INFO, WARNING, ERROR, or CRITICAL
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=log_filename
)

# variable for writing out logs
logger = logging.getLogger()

# loading the environment that contains our API Keys
load_dotenv()

# setting and calling variables from our environment that houses the API keys
AMP_API_KEY = os.getenv('AMP_API_KEY')
AMP_SECRET_KEY = os.getenv('AMP_SECRET_KEY')

# setting a start date for our events data can go back x amount of days starting midnight
days_back = 1
start_date = datetime.now() - timedelta(days = days_back)
start_date = start_date.strftime('%Y%m%dT00')

# setting an end date for our events data i.e. today
end_date = datetime.now()
end_date = end_date.strftime('%Y%m%dT23')

# this is an argument that will be inserted into our API call to get data for the from our dates set
params = {
    "start": start_date,
    "end": end_date
}

# timestamp for the when the script it is run
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

# making a directory for the data zip folders
data_dir = "data_zip_files"
os.makedirs(data_dir, exist_ok=True)

# variable for the data file name
data_name = os.path.join(data_dir, f"amplitude_data_{timestamp}")

# API url and endpoint
url = 'https://analytics.eu.amplitude.com/api/2/export'

# calling the API
response = requests.get(url, params=params, auth=(AMP_API_KEY, AMP_SECRET_KEY))
logger.info(f"API Call Response Code: '{response.status_code}'")

if response.status_code == 200: # if we get a 200 response (good) then save the data as a zip file
    data = response.content
    logger.info("Data retrieved successfully.")
    logger.info(f"Saving data to {data_name}.zip")
    print("Data retrieved successfully.")
    print(f"Saving data to {data_name}.zip")
    with open(f"{data_name}.zip", 'wb') as file:
        file.write(data)
    logger.info(f"Data saved to {data_name}.zip")
    print(f"Data saved to {data_name}.zip")
else:
    print(f'Error {response.status_code}: {response.text}') # otherwise print the status code and the error
    logger.error(f"API Call Error '{response.status_code}: {response.text}'")

logger.info("Process Finished")
print("Process Finished")
```

A key consideration of the script is this part:

```python
# setting a start date for our events data can go back x amount of days starting midnight
days_back = 1
start_date = datetime.now() - timedelta(days = days_back)
start_date = start_date.strftime('%Y%m%dT00')
```

As the data, when unzipping the jsons later down the line, is in hourly increments then it is best to limit the `days_back` variable to a few days to prevent too much data being pulled.

## JSON Unzipping

The following `amplitude_zip_process.py` script is what takes all of the json files from the data zip folder:

```python
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
        logger.info("There is 1 zip file to process")
    else:
        logger.info(f"There are {len(amplitude_zip_process_files)} zip files to process")

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

                    json_base_name = file.replace('.gz', '')

                    final_json_path = os.path.join(unzipped_dir, json_base_name)

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
```

The archive section of the code:

```python
        # move processed zip file to archive
        shutil.move(data_zip_path, os.path.join(archive_dir, data_zip_name))
        logger.info(f"Successfully processed and archived {data_zip_name}")

    except Exception as e:
        logger.info(f"An error occured processing {data_zip_name}: {e}. Leaving {data_zip_name} in place")
```

acts as a final part of cold storage. Some additions would require removing the old data zip folders based on a certain time period (e.g. x amount of days from today will be removed).

# 2. Load

This section entails of taking the json files after being unzipped into an s3 bucket. First the creation and configuration of the s3 bucket was done first and then from there was able to load all of the data into it.

## AWS s3 Bucket Set-up

![AWS s3 bucket Setup](https://github.com/LorenzNacilla/Amplitude-Events-Extract/blob/main/images/AWS%20s3%20bucket%20Setup.png)
This diagram overall highlights the set up of the s3 bucket:
- Created the KMS (Key Management Service) key which contains the ARN (Amazon Resource Name) and is used in creation of the s3 bucket.
- Created the s3 bucket and ensuring that public access is blocked, as well that it is encrypted using the ARN from the KMS key as mentioned above.
- An IAM (Identity and Access Management) policy was created which set privileges to our s3 buckket (e.g. Read/Write to Bucket).
- A user was created where the created policy above is attached to it. As a result of creaitng the user, I was able to get the access key and secret key from it which essentially acts as authentication to use the bucket - allowing to put data in the bucket.
- A role was also created and the same policy is attached to it as well. Difference between the user created and the role is that the role allows us to be able to put the data into snowflake from s3.

## Snowflake Storage Integration, Stages, and Snowpipes

![Snowflake Storage Integration and Staging](https://github.com/LorenzNacilla/Amplitude-Events-Extract/blob/main/images/Snowflake%20Storage%20Integration%20and%20Staging.png)
Now that the s3 bucket and any AWS configurations have been set up, the next phase is to create a snowflake storage integration and then stages. The storage integration is what handles the authentication between the s3 bucket and AWS configurations we set up earlier. The stage(s) on the other hand is what reads the data from a specific point/folder within the bucket, so it picks up data from there only rather than getting everything from the bucket (unless you have no further folders/sub-directories in your bucket).

The syntax below is what was used to create the storage integration:
```sql
CREATE OR REPLACE STORAGE INTEGRATION <insert storage integration name>
  TYPE = EXTERNAL_STAGE
  STORAGE_PROVIDER = 'S3'
  ENABLED = TRUE
  STORAGE_AWS_ROLE_ARN = '<insert arn>'
  STORAGE_ALLOWED_LOCATIONS = ('<insert bucket name>');
```

Then by running
```sql
DESC INTEGRATION <snowflake storage integration name>;
```
Find the details for ```STORAGE_AWS_IAM_USER_ARN``` and ```EXTERNAL_ID```, then go back to your IAM role and edit the trust policy by replacing the ARN and External ID there. After doing so, we should be able to move on to creating our stages.

First, a file format was created so snowflake knows what kind of data is being read into it.
```sql
CREATE OR REPLACE FILE FORMAT <file format name>
TYPE = 'JSON'
STRIP_OUTER_ARRAY = TRUE;
```

Then the stage itself was created.
```sql
CREATE OR REPLACE STAGE <stage name>
STORAGE_INTEGRATION = <storage integration name>
URL = 's3://<bucket name>/<folder name>/'
FILE_FORMAT = <file format name>;
```

The table for the raw data itself.
```sql
CREATE OR REPLACE TABLE <table name> (
  json_data VARIANT
);
```

Then a snowpipe was made so that when there's new data in the s3 bucket, then this would then be fed straight into the table(s) made.
```sql
CREATE OR REPLACE PIPE <pipe name>
AUTO_INGEST = TRUE
AS
COPY INTO <table name>
FROM @<stage name>
FILE_FORMAT = (FORMAT_NAME = <file format name>)
ON_ERROR = 'CONTINUE';
```

## Python Load into s3

The following script was used to load all of the unzipped json data files into the s3 bucket that was created:

```python
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

# making directories
os.makedirs(logs_dir, exist_ok = True)

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
print("Beginning s3 upload")
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

        aws_file_destination = "python-import/" + filename

        try:
            s3_client.upload_file(
                local_file_path
                , bucket_name
                , aws_file_destination
            )
            logger.info(f"Uploaded {local_file_path} to s3://{bucket_name}/{aws_file_destination}")

            os.remove(local_file_path)
            logger.info(f"Removed file: {local_file_path}")

        except Exception as e:
            logger.error(f"Failed during upload/removal for {local_file_path}: {e}")

    logger.info("s3 upload finished.")
    print("s3 upload finished.")
```

With the snowpipe made before, running the script should load data into snowflake as well.

# 3. Transform

Now that the data has been loaded into snowflake, the next phase was to start transforming it. The transformation can be done in either snowflake or dbt.

## Schema

First before the transformation is done, I designed a quick schema to answer some following business questions/use cases:
- What journeys are users taking on the website?
- Can we associate the IP address of a user with a particular company, so we can see which companies are visiting the website?
- Is a user making repeated clicks on the website?
- Is there any evidence that a user finds the menu on the UK website confusing?

![Amplitude Schema](https://github.com/LorenzNacilla/Amplitude-Events-Extract/blob/main/images/Amplitude%20Schema.png)

The Sessions/Events table would be the facts table which tells that for every session a user is on within the website, the series of events respectively. The locations and devices table are dimensions tables. Locations being able to tell us where a user is from - allowing analysis where in the world people are viewing the website, and devices being able to find out what device people are on mainly when viewing the website but with further analysis allowing to see if any particular devices people have struggle with on the website via repeated clicks.

## dbt
First part was creating the yaml file for the source data. The yml file below defines the one table as our source data:
```yaml
version: 2

sources:
  - name: amplitude_data
    database: TIL_DATA_ENGINEERING
    schema: LORENZNACILLA_STAGING
    tables:
      - name: LORENZNACILLA_AMPLITUDE_EVENTS_RAW_PYTHON
        columns:
          - name: JSON_DATA
            data_type: variant
```
