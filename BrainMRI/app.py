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

import json


app = Flask(__name__)

datadir = ""  # 定义全局变量


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    global datadir  # 声明使用全局变量
    data = request.get_json()
    file_path = data.get('path')

    if file_path and os.path.isdir(file_path):
        datadir = file_path  # 更新全局变量
        print(datadir)
        return jsonify({'message': 'data path set successfully', 'datadir': datadir})
    else:
        return jsonify({'message': 'Invalid data path'}), 400

@app.route('/clear', methods=['POST'])
def clear():
    global datadir
    if datadir:
        datadir = ""  # 清空全局变量
        print(datadir)
        return jsonify({'message': 'data path cleared successfully'})
    else:
        return jsonify({'message': 'No data path to clear'}), 400




running_commands = set()

@app.route('/runcmd', methods=['POST'])
def run_command():
    data = request.get_json()
    command = data.get('command')


    # 清空 progress.txt 文件
    with open('progress.txt', 'w') as f:
        f.write(" 0 / 13 ")
    
    if command:
        if command in running_commands:
            return jsonify({'error': '该命令正在运行！'}), 400
        
        running_commands.add(command)
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            return jsonify({'output': result.stdout, 'error': result.stderr}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        finally:
            running_commands.remove(command)
    return jsonify({'error': 'No command provided'}), 400


@app.route('/get-progress', methods=['GET'])
def get_progress():
    try:
        with open('progress.txt', 'r') as f:
            progress = f.read()
        return jsonify({'progress': progress})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 在一个新线程中运行 Flask 应用程序的函数
def run_flask_app():
    app.run(debug=True, use_reloader=False)


run_flask_app()