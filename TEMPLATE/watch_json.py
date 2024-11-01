import os
import time
import json
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, Any  # 解析json用
from update_db import DBStatus
from logger import setup_logger
# load logger
logger = setup_logger('watch_json')
# load env
load_dotenv()
REPORT_DONE_PATH = os.getenv("REPORT_DONE_PATH")
REPORT_ERROR_PATH = os.getenv("REPORT_ERROR_PATH")
REPORT_JSON_PATH = os.getenv("REPORT_JSON_PATH")
RPT_STAT_PARSE_ERR = os.getenv("RPT_STAT_PARSE_ERR")
RPT_STAT_DONE = os.getenv("RPT_STAT_DONE")
RPT_STAT_NOTCLEAR = os.getenv("RPT_STAT_NOTCLEAR")
# 确保 DIR 存在
Path(REPORT_DONE_PATH).mkdir(parents=True, exist_ok=True)
Path(REPORT_JSON_PATH).mkdir(parents=True, exist_ok=True)
Path(REPORT_ERROR_PATH).mkdir(parents=True, exist_ok=True)
# load db function
db_status = DBStatus()
# 指定文件的扩展名
image_extensions = {'.json'}
# %%
class JsonHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            file_path = event.src_path
          
            logger.info("----------------------------------")
            logger.info(f"Detected new JSON file: {file_path}")

            self.process_json(file_path)

    def process_json(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
            report_id = Path(file_path).stem

            # 解析 JSON 数据            
            self.parse_report(file_path, report_id, data)

    def parse_report(self, file_path, report_id, data):      
        try:
            # 初始化结果字典
            result = {
                "report_cat": "", #medical_report or lab_test
                "report_type": "",
                "report_date": "",
                "patient_info": {},
                "report_info": {}
            }

            if "medical_report" in data[0]:        
                
                report = data[0]["medical_report"]
                result["report_cat"] = "medical_report"
                result["report_type"] = report.get("test_info", {}).get("test_type", "")
                result["report_date"] = report.get("test_info", {}).get("report_date", "")        
                result["patient_info"] = report.get("patient_info", {})
                result["report_info"] = report.get("test_info", {})

            elif "lab_test" in data[0]:       
                
                report = data[0]["lab_test"]
                result["report_cat"] = "lab_test"
                result["report_type"] = report.get("test_info", {}).get("test_type", "")
                result["report_date"] = report.get("test_info", {}).get("report_date", "")
                result["patient_info"] = report.get("patient_info", {})
                result["report_info"] = report.get("test_info", {})

            # 如果 result 为空，更新数据库状态并移动文件
            if not any(result.values()):
                logger.warning(f"ID:{report_id} 结果为空，图片不清晰 移动到 reports_error 文件夹")
                db_status.update_status(report_id, RPT_STAT_NOTCLEAR)
                logger.error(f"更新 ID:{report_id} 資料庫狀態為 {RPT_STAT_NOTCLEAR} (图片不清晰)")

                # 移动到 reports_error 文件夹
                file_path = Path(file_path)
                if file_path.exists():
                    try:
                        shutil.move(file_path, Path(REPORT_ERROR_PATH) / file_path.name)
                        logger.info(f"Move {file_path.name} to error folder: {REPORT_ERROR_PATH}")
                    except Exception as e:
                        logger.error(f"Error moving json file to reports_error folder: {e}")
                else:
                    logger.warning(f"File {file_path.name} does not exist. Skipping move.")
                return  # 结束当前方法
            
            # 更新 db
            db_status.update_status(report_id, RPT_STAT_DONE, result)
            logger.info(f"更新 ID:{report_id} 資料庫狀態為 {RPT_STAT_DONE} (正常完成) 以及相關欄位")

            # 移动 json 到 done 資料夾
            file_path = Path(file_path)
            if file_path.exists():
                try:
                    shutil.move(file_path, Path(REPORT_DONE_PATH) / file_path.name)
                    logger.info(f"Move {report_id} to {REPORT_DONE_PATH} Folder")
                except Exception as e:
                    logger.error(f"Error moving json file to done directory: {e}")
            else:
                logger.warning(f"File {report_id} does not exist. Skipping move.")




        except Exception as e:
            # 解析失败 更新数据库状态为4
            logger.error(f"ID:{report_id} 解析失败: {e}")

            db_status.update_status(report_id, RPT_STAT_PARSE_ERR)
            logger.error(f"更新 ID:{report_id} 資料庫狀態為 {RPT_STAT_PARSE_ERR} (解析失敗)")

            # 移動失敗的json到error 資料夾
            file_path = Path(file_path)
            if file_path.exists():
                try:
                    shutil.move(file_path, Path(REPORT_ERROR_PATH) / file_path.name)                    
                    logger.info(f"Move  {file_path.name} to error folder: {REPORT_ERROR_PATH} ")
                except Exception as e:
                    logger.error(f"Error moving json file to error folder: {e}")
            else:
                logger.warning(f"File {file_path.name} does not exist. Skipping move.")

# %%
def process_existing_files():
    for file in Path(REPORT_JSON_PATH).glob('*'):
        if file.is_file() and file.suffix.lower() in image_extensions:       
            logger.info("----------------------------------")
            logger.info(f"Processing existing file: {file}")

            event_handler.process_json(str(file))

# %%
if __name__ == "__main__":
    event_handler = JsonHandler()
    observer = Observer()
    observer.schedule(event_handler, REPORT_JSON_PATH, recursive=False)
    observer.start()

    logger.info("Watching for JSON files...")

    process_existing_files()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
