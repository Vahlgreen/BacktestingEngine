from datetime import timedelta, datetime
import os

def DateDiff(start: str, end: str) -> int:
    # returns number of days between two dates
    return (datetime.strptime(end, '%Y-%m-%d').date() - datetime.strptime(start,'%Y-%m-%d').date()).days

def SubtractDays(date: str, days: int) -> str:
    # returns difference in days between two dates
    return (datetime.strptime(date, '%Y-%m-%d').date() - timedelta(days=days)).strftime('%Y-%m-%d')

def AbsPath(pathFromScript: str) -> str:
    #returns the absolute path to file location (e.g. functions.py)
    script_directory = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_directory, pathFromScript)

def ResetLogs(paths: list) -> None:
    # removes files given in input list
    for path in paths:
        script_directory = os.path.dirname(os.path.abspath(__file__))
        data_file = os.path.join(script_directory, path)
        if os.path.exists(data_file):
            os.remove(data_file)