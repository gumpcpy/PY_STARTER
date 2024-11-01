'''
Author: gumpcpy gumpcpy@gmail.com
Date: 2024-09-20 23:51:50
LastEditors: gumpcpy gumpcpy@gmail.com
LastEditTime: 2024-09-23 13:05:58
Description: 
'''
import logging

def setup_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # 创建文件处理器
    file_handler = logging.FileHandler('./log/process_log.log')
    file_handler.setLevel(logging.INFO)

    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # 设置日志格式
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # 添加处理器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
