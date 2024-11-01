'''
Author: gumpcpy gumpcpy@gmail.com
Date: 2024-09-21 09:31:08
LastEditors: gumpcpy gumpcpy@gmail.com
LastEditTime: 2024-09-21 11:37:34
Description: 
'''
import requests,os
from dotenv import load_dotenv
from logger import setup_logger

# load logger
logger = setup_logger('update_database')

class DBStatus:
    def __init__(self):
        load_dotenv()
        self.API_TOKEN = os.getenv("API_TOKEN")
        self.UPD_API_URL = os.getenv("UPD_API_URL")

    def update_status(self, report_id, status, additional_data=None):
        url = self.UPD_API_URL
        payload = {
            'id': report_id,
            'status': status,
            'additional_data': additional_data or {},
            'api_key': self.API_TOKEN  
        }

        response = requests.post(url, json=payload)
        # response = requests.get(url, json=payload)

        if response.status_code == 200:
            print("Status updated successfully")
            logger.info("Status updated successfully")
        else:
            print(f"Failed to update status: {response.status_code}, {response.text}")
            logger.error(f"Failed to update status: {response.status_code}, {response.text}")




