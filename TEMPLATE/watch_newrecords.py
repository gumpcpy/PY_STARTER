'''
Author: gumpcpy gumpcpy@gmail.com
Date: 2024-09-24 12:20:22
LastEditors: gumpcpy gumpcpy@gmail.com
LastEditTime: 2024-10-10 10:21:32
Description: 
'''
import time
import os
import requests
from dotenv import load_dotenv
from update_db import DBStatus
from pathlib import Path
from logger import setup_logger
# load logger
logger = setup_logger('watch_newrecords')
# load env
load_dotenv()
GET_RPT_POLL_API = os.getenv("GET_RPT_POLL_API")
FILE_URL = os.getenv("FILE_URL")
REPORT_PATH = os.getenv("REPORT_PATH")
RPT_STAT_DOWNLOAD = os.getenv("RPT_STAT_DOWNLOAD")
# load db
db_status = DBStatus()
# 确保 DIR 存在
Path(REPORT_PATH).mkdir(parents=True, exist_ok=True)

def poll_images():

    url = GET_RPT_POLL_API
    logger.info(f"URL:{url}")
    while True:
        try:
            response = requests.get(url)
            images = response.json()

            if images:
                logger.info(f"Found {len(images)} new images to process.")
                for image in images:
                    process_image(image['id'], image['filename'])
            else:
                logger.info("No new Reports. Waiting...")
            
            # 控制輪詢間隔
            time.sleep(5)  # 每次請求後等待 1 秒
        except Exception as e:
            logger.error(f"Error: {e}")
            time.sleep(5)  # 出現錯誤時等待 5 秒後重試

def process_image(id, filename):
    try:
        # 1 下载图片 
        image_url = FILE_URL + filename
        response = requests.get(image_url)                
        logger.info(f"Downloading ID:{id} File:{filename}")
        
        # ext 找到最后一个点的索引
        last_dot_index = filename.rfind('.')
        # ext 如果找到了点，返回点之后的部分；否则返回空字符串
        ext = filename[last_dot_index:] if last_dot_index != -1 else ''
        # save file to downloads 用 report id 當檔名
        image_path = os.path.join(REPORT_PATH, f'{id}{ext}')
        with open(image_path, 'wb') as f:
            f.write(response.content)
        logger.info(f"Download ID:{id} File:{filename}----OK")
                        
        # 2 update db status
        db_status.update_status(id, RPT_STAT_DOWNLOAD)                
        logger.info(f"下載完成 Update DB Status:{RPT_STAT_DOWNLOAD} for ID:{id}")              

    except requests.RequestException as e:
        logger.error(f"Error downloading file {filename}: {e}")
        
    except Exception as e:
        logger.error(f"Error processing report, id: {id}, error: {e}")


if __name__ == '__main__':
    poll_images()
