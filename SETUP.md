<!--
 * @Author: gumpcpy gumpcpy@gmail.com
 * @Date: 2024-11-01 20:06:13
 * @LastEditors: gumpcpy gumpcpy@gmail.com
 * @LastEditTime: 2024-11-01 20:58:44
 * @Description: 
-->
## 如何建立一個新的python專案

(1)
下載github PYTHON_STARTER

(2)
進入資料夾 
建立環境 my_env改成我要的環境名稱 版本用你想要用的
    
    conda create -n my_env python=3.11

啟動環境

    conda activate my_env

安裝我需要的包 conda 先試試看 不行才用 pip
    
    conda install 我需要的包

進入TEST 先首要建立我要的主要功能 main.py

編輯好了 可以使用了 就去外面 建立真的 這時可以改造我原有的模板的程式片段


## 修改模板
## 建立main.py

## 導出 requirement
    
    pip freeze > requirements.txt

導入 requirement

    pip install -r requirements.txt

    
## 上傳github

git init
git add README.md
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/gumpcpy/PY_STARTER.git

git push -u origin main


到github上建立一個repository
git remote add origin https://github.com/gumpcpy/PY_STARTER.git
git branch -M main
git push -u origin main
