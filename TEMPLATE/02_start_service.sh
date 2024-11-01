#!/bin/bash
###
 # @Author: gumpcpy gumpcpy@gmail.com
 # @Date: 2024-09-20 23:40:09
 # @LastEditors: gumpcpy gumpcpy@gmail.com
 # @LastEditTime: 2024-10-09 10:15:32
 # @Description: 
 # 要終止這些後台進程，要 killall python 或者 ps -e | grep python 一個個kill (kill -9 process_id)
### 

cd /Users/gump/Documents/_Proj/health_tracker/MROCR_1_1
conda activate health_tracker
# 啟動 Flask 
python app.py &
# 開啟 監控 下載新的報告
python watch_newrecords.py &
# 開啟 監聽 REPORT_PATH 下有新的報告就呼叫 OCR
python watch_report.py &
# 開啟 監聽 REPORT_JSON_PATH 下有新的json就進行解析回傳DB
python watch_json.py &
# 等待所有后台进程
wait
