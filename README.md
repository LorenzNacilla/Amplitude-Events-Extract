# Amplitude-Events-Extract

This repo looks into extracting events data from the Amplitude API. There were two methods in calling the API - one using airbyte to call the API itself and then landing it in an azure blob storage, and the other with a python script. This repo mainly contains the python script to call the API but the method with airbyte and azure blob storage is used.

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

# 1. Extract

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

## Considerations

A key consideration of the script is this part:

```python
# setting a start date for our events data can go back x amount of days starting midnight
days_back = 1
start_date = datetime.now() - timedelta(days = days_back)
start_date = start_date.strftime('%Y%m%dT00')
```

As the data, when unzipping the jsons later down the line, is in hourly increments then it is best to limit the `days_back` variable to a few days to prevent too much data being pulled.

# 2. Load

# 3. Transform
