#!/bin/python3
import os
import json
import requests

def remove_files (list):
    for file in list:
        os.remove(file)

def check_duty_eng():
    if os.path.exists('duty.json'):
        with open ('duty.json', 'r', encoding='utf8') as duty_file:
            duty_eng = json.load(duty_file)
        return duty_eng
    else:
        return None
