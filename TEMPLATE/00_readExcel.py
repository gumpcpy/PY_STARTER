'''
Author: gumpcpy gumpcpy@gmail.com
Date: 2024-11-01 22:57:05
LastEditors: gumpcpy gumpcpy@gmail.com
LastEditTime: 2024-11-01 23:06:44
Description: 
'''
'''
執行python test.py
會要求拖入一個excel
以及拖入一個含有圖片的folder
本程式會根據excel中 Filename 的欄位
把folder裡面符合名稱的圖片放入Excel Image的欄位裡。
'''

import os
import pandas as pd

def read_excel(file_path):
    df = pd.read_excel(file_path)
    print(df)


# %%
input_excel = input("請輸入有Image和Filename兩個欄位的excel").strip()
# folder_path = input("拖入截圖folder: ").strip()

print(f"excel:{input_excel}")
# print(f"folder:{folder_path}")

if not os.path.exists(input_excel):
    print("Error: Excel不存在")
    exit()

# if not os.path.exists(folder_path):       
#     print("Error: 截圖路徑不存在:", folder_path)
#     exit()

read_excel(input_excel)

   


