import requests
import os
import zipfile
import gzip
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

AMP_API_KEY = os.getenv('AMP_API_KEY')
AMP_SECRET_KEY = os.getenv('AMP_SECRET_KEY')

start_date = datetime.now() - timedelta(days= 1)
start_date = start_date.strftime('%Y%m%dT00')
# print(start_date)
# print(type(start_date))

end_date = datetime.now()
end_date = end_date.strftime('%Y%m%dT23')
# print(end_date)
# print(type(start_date))

params = {
    "start": start_date,
    "end": end_date
}
#print(params)

url = 'https://analytics.eu.amplitude.com/api/2/export'

response = requests.get(url, params=params, auth=(AMP_API_KEY, AMP_SECRET_KEY))

if response.status_code == 200:
    data = response.content
    print("Data retrieved successfully.")
    with open('amplitude_data.zip', 'wb') as file:
        file.write(data)
else:
    print(f'Error {response.status_code}: {response.text}')
