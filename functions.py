from datetime import timedelta, datetime
import os
import numpy as np

def date_difference(start: str, end: str) -> int:
    # returns number of days between two dates
    return (datetime.strptime(end, '%Y-%m-%d').date() - datetime.strptime(start,'%Y-%m-%d').date()).days

def subtract_days(date: str, days: int) -> str:
    # returns difference in days between two dates
    return (datetime.strptime(date, '%Y-%m-%d').date() - timedelta(days=days)).strftime('%Y-%m-%d')

def get_absolute_path(path_from_script: str) -> str:
    #returns the absolute path to file location (e.g. functions.py)
    script_directory = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_directory, path_from_script)

def reset_logs(paths: list) -> None:
    # removes files given in input list
    for path in paths:
        script_directory = os.path.dirname(os.path.abspath(__file__))
        data_file = os.path.join(script_directory, path)
        if os.path.exists(data_file):
            os.remove(data_file)