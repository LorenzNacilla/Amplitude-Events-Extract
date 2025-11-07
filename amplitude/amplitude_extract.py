import requests
import os
import zipfile
import gzip
import logging
from dotenv import load_dotenv
from datetime import datetime, timedelta

# log filename for when the script is run
log_filename = f"logs/amplitude_extract_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

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

# setting a start date for our events data can go back x amoubnt of days starting midnight
days_back = 3
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
#print(params)

# API url and endpoint
url = 'https://analytics.eu.amplitude.com/api/2/export'

# variable for the data file name
data_name = 'amplitude_data'

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




