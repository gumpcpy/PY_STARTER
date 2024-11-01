'''
Author: gumpcpy gumpcpy@gmail.com
Date: 2024-11-01 22:35:11
LastEditors: gumpcpy gumpcpy@gmail.com
LastEditTime: 2024-11-01 22:50:18
Description: 

    我想要輸入一個文件夾
    把文件的名稱寫入csv放在執行py文件旁邊

'''
import os
import csv
from datetime import datetime

filenameList = []

def process_folder(folder_path):
    for filename in os.listdir(folder_path):
        # print(filename)
        filenameList.append(filename)

    return filenameList

def show_date():
    show_time = datetime.now().strftime('%Y-%m-%d')
    print(show_time)

def write_csv(result):
    csv_path = "./test.csv"
    with open(csv_path,'w',newline='',encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Filename'])
        for filename in result:
            csvwriter.writerow([filename])

        
    print(f"CSV文件已保存: {csv_path}")

while True:
    input_folder = input("請拖入要處理的資料夾:").strip()

    if os.path.isdir(input_folder):
        break
    else:
        print("資料夾不存在，重新輸入")
        
result = process_folder(input_folder)
write_csv(result)

