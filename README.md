# Amplitude-Events-Extract

This repo looks into extracting events data from the Amplitude API. There were two methods in calling the API - one using airbyte to call the API itself and then landing it in an azure blob storage, and the other with a python script. This repo mainly contains the python script to call the API but the method with airbyte and azure blob storage is used.

## ➡️ General Data Flow

![General Flow](https://github.com/LorenzNacilla/Amplitude-Events-Extract/blob/main/images/General%20Flow.png)
This is a general flow of the project. For the time being this is looking at more of the API call and the storing it into a bucket which is more for the airbyte flow shown below.

![Airbyte Flow](https://github.com/LorenzNacilla/Amplitude-Events-Extract/blob/main/images/Airbyte%20Flow.png)
This is a diagram that highlights the method of using airbyte and azure blob storage. A big pro of airbyte is that it is no-code and makes use of a UI.

![Python Flow](https://github.com/LorenzNacilla/Amplitude-Events-Extract/blob/main/images/Python%20Flow.png)
