from itertools import dropwhile
import numpy as np
import subprocess
import fnmatch
import shutil
import codecs
import math
import sys
import os
from flask import Flask, render_template, jsonify, request
import threading
import logging
import time

import json


datadir = ""  # 定义全局变量



def setup_logger(logger_name, file_name):
    # 创建 logger 对象
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    # 创建文件处理器，并设置日志级别和文件名
    file_handler = logging.FileHandler(file_name)
    file_handler.setLevel(logging.DEBUG)

    # 将文件处理器添加到 logger 对象中
    logger.addHandler(file_handler)

    return logger

# 使用函数设置日志记录器
logger = setup_logger('infomation', 'log.log')

def step1(root_subject):
    print("Executing step 1 for:", root_subject)


def step2(root_subject):
    print("Executing step 2 for:", root_subject)


def step3(root_subject):
    print("Executing step 3 for:", root_subject)


def step4(root_subject):
    print("Executing step 4 for:", root_subject)


def step5(root_subject):
    print("Executing step 5 for:", root_subject)


def step6(root_subject):
    print("Executing step 6 for:", root_subject)


def step7(root_subject):
    print("Executing step 7 for:", root_subject)


def step8(root_subject):
    print("Executing step 8 for:", root_subject)


def step9(root_subject):
    print("Executing step 9 for:", root_subject)


def step10(root_subject):
    print("Executing step 10 for:", root_subject)


def step11(root_subject):
    print("Executing step 11 for:", root_subject)


def step12(root_subject):
    print("Executing step 12 for:", root_subject)


def step13(root_subject):
    print("Executing step 13 for:", root_subject)


def FiberGeneration(root_subject):
    
    steps = [
        step1, step2, step3, step4, step5,
        step6, step7, step8, step9, step10,
        step11, step12, step13
    ]

    for i, step in enumerate(steps):
        step(root_subject)
        print(f"Currently on step {i + 1} of {len(steps)}.")

        with open('progress.txt', 'w') as f:
            f.write(f" {i + 1} / {len(steps)} ")

        time.sleep(2)


if __name__ ==  '__main__':
    try:
        
        FiberGeneration(datadir)
        
    except Exception as exception:
        logger.exception(exception)
        raise