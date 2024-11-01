#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Author: gumpcpy gumpcpy@gmail.com
Date: 2024-04-16 23:16:11
LastEditors: gumpcpy gumpcpy@gmail.com
LastEditTime: 2024-04-18 14:05:51
Description: 

version: v03

打開console，安裝

pip3 install pandas
pip3 install Pillow
pip3 install openpyxl

執行：python3 pasteImg2Excel.py 

會根據現有的excel中的Clipname欄位，
去snap folder裡找名字一樣的圖檔，把它縮小後，
放入Excel的Image格子裡。並調整欄位高度
注意：
所以excel裡面需要有Clipname欄位還有Image欄位。注意拼寫要正確。

版本修改：
v02 修正路徑含有空格會不能用的錯誤。2024 04 17
v03 RGBA 不能存為JPG 所以先轉存為RGB 再存。 2024 04 18
'''
import shlex
import shutil
import os
import pandas as pd
from PIL import Image
from openpyxl import load_workbook
from openpyxl.drawing.image import Image as xlImage


excel_file_t = input("拖入Excel檔案: ").strip()

# 使用shlex.split()来解析路径
excel_file_s = shlex.split(excel_file_t)
excel_file = os.path.join(*excel_file_s)

# 输出解析后的路径
print("解析后的路径:", excel_file)

# Check if the entered Excel file exists
if not os.path.exists(excel_file):
    print("Error: Excel不存在")
    exit()

# Make a copy of the original Excel file
backup_excel_file = os.path.splitext(excel_file)[0] + "_backup.xlsx"
shutil.copy2(excel_file, backup_excel_file)
print("已經將原本Excel檔案備份:", backup_excel_file)

# Prompt the user for the path to the 'snap' folder
folder_path = ""
while True:
    folder_path_t = input("拖入截圖folder: ").strip()

    # 使用shlex.split()来解析路径
    folder_path_s = shlex.split(folder_path_t)
    folder_path = os.path.join(*folder_path_s)

    if not folder_path.endswith("/"):
        folder_path += "/"
   
    if os.path.exists(folder_path):
        break
    else:
        print("Error: 截圖路徑不存在:", folder_path)
   
# 讀取Excel檔案
df = pd.read_excel(excel_file.strip())

# 存儲圖片文件的資料夾路徑
output_folder = "snap_tmp"

# 創建存儲圖片文件的資料夾
os.makedirs(output_folder, exist_ok=True)

# 開啟現有的Excel檔案
wb = load_workbook(excel_file)
ws = wb.active

# Find the index of the "Image" column
image_column_index = None
for col in range(1, df.shape[1] + 1):
    if df.columns[col - 1] == "Image":
        image_column_index = col
        break

# Ensure "Image" column exists in the DataFrame
if image_column_index is None:
    print("Error: 'Image' column not found in the Excel file.")

# Get the column letter of the "Image" column (assuming it's the one before the specified image_column_index)
image_column_letter = chr(65 + image_column_index - 1)

# 處理每一個檔案名稱
for index, row in df.iterrows():
    filename = row["Clipname"]
    # 在資料夾中尋找以該檔名開頭的圖片檔案
    matching_files = [f for f in os.listdir(
        folder_path) if f.startswith(filename)]
    if matching_files:
        # 假設只有一個符合的檔案，取第一個
        matched_file = matching_files[0]
        file_path = os.path.join(folder_path, matched_file)

        # 讀取圖片
        img = Image.open(file_path)
        # 調整圖片寬度為250
        width_percent = (250 / float(img.size[0]))
        height_size = int((float(img.size[1]) * float(width_percent)))
        img = img.resize((250, height_size), Image.LANCZOS)
      
        # 將圖片保存為文件
        output_file_path = os.path.join(output_folder, f"{filename}.jpg")
        img = img.convert("RGB")
        img.save(output_file_path)

        # 將圖片插入到Excel的指定儲存格中
        img = xlImage(output_file_path)
      
        # img.anchor = f"A{index+2}"  # 在A列插入圖片，從第二行開始
        img.anchor = f"{image_column_letter}{index + 2}"

        ws.add_image(img)

        # 獲取插入的圖片的高度
        img_height_pixels = img.height
        # 設置插入圖片所在行的高度，將其設置為圖片的高度
        ws.row_dimensions[index+2].height = img_height_pixels / \
            1.333  # 將像素轉換為點，1點=1/72英寸
    

# 儲存修改後的Excel檔案
wb.save(excel_file)

print("Excel 插入圖片處理完畢")

# Delete the temporary folder
shutil.rmtree(output_folder)
