from datetime import timedelta, datetime
from scipy.signal import find_peaks
import os
import numpy as np
import pandas as pd


def date_difference(start: str, end: str) -> int:
    """Returns number of days between two dates"""
    return (datetime.strptime(end, '%Y-%m-%d').date() - datetime.strptime(start,'%Y-%m-%d').date()).days

def subtract_days(date: str, days: int) -> str:
    """Returns difference in days between two dates"""
    return (datetime.strptime(date, '%Y-%m-%d').date() - timedelta(days=days)).strftime('%Y-%m-%d')

def get_absolute_path(path_from_script: str) -> str:
    """Returns the absolute path to file location (e.g. functions.py)"""
    script_directory = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_directory, path_from_script)

def reset_logs(paths: list):
    """Removes files given in input list"""
    for path in paths:
        script_directory = os.path.dirname(os.path.abspath(__file__))
        data_file = os.path.join(script_directory, path)
        if os.path.exists(data_file):
            os.remove(data_file)

def mean_list(inp_list: list) -> float:
    """native python is faster than numpy for small lists (>150 entries)"""
    return sum(inp_list)/len(inp_list)

def exponential_moving_average(data: np.ndarray, look_back_period: int) -> np.ndarray:
    """returns a vector with ewma of input data. Equivalent to pandas ewm(adjust=False).mean()"""

    # parameters for emwa
    alpha=1/look_back_period
    alpha_rev = 1 - alpha
    n = len(data)
    pwo = alpha * alpha_rev ** (n - 1)
    pows = alpha_rev ** (np.arange(n + 1))
    scale_arr = 1 / pows[:-1]


    # average gain
    first_observation = data[np.logical_not(np.isnan(data))][0]
    offset = first_observation*pows[1:]
    #offset = data[0]*pows[1:]
    mult = data*pwo*scale_arr
    cumsums = np.cumsum(mult)
    ewma = offset + cumsums*scale_arr[::-1]

    return ewma

def directional_movement_index(data: pd.DataFrame, look_back_period: int, current_date: str) -> np.ndarray:
    """Returns a vector with dmi for each timestep in isolated range"""

    # Isolate date range
    current_date_index = np.where(data["Date"].values == current_date)[0][0]
    data_high = trim_stock_data(data["High"].values,current_date_index)
    data_low = trim_stock_data(data["Low"].values,current_date_index)
    data_close = trim_stock_data(data["Close"].values,current_date_index)


    hl = data_high-data_low
    hc = np.abs(shifted_array_difference(data_high, data_close, 2))
    lc = np.abs(shifted_array_difference(data_low, data_close, 2))
    tr = np.nanmax(np.column_stack((hc, hl, lc)),axis=1)

    atr = exponential_moving_average(tr,look_back_period)
    hph = shifted_array_difference(data_high,data_high,2)
    pll = shifted_array_difference(data_low,data_low,1)

    pdx = np.where((hph>pll) & (hph>0), hph, 0)
    mdx = np.where((hph<pll) & (pll>0), pll, 0)

    spdm = exponential_moving_average(pdx,look_back_period)
    smdm = exponential_moving_average(mdx,look_back_period)

    pdmi = (spdm/atr)*100
    mdmi = (smdm/atr)*100

    dx = (np.abs(pdmi - mdmi) / (pdmi + mdmi)) * 100

    adx = exponential_moving_average(dx[np.logical_not(np.isnan(dx))], look_back_period)
    return adx

def shifted_array_difference(arr1: np.array, arr2: np.array, shifted_argument: int) -> np.array:
    """
    Computes the difference of arrays with one array shifted.
    shifted_argument: which input argument to shift
    """

    return_arr = np.zeros_like(arr1)

    if shifted_argument == 2:
        difference = arr1[1:]-arr2[:-1]
    else:
        difference = arr1[:-1]-arr2[1:]

    return_arr[1:] = difference

    return return_arr

def trim_stock_data(arr: np.array, current_date_index: int, max_obs: int = 50):
    """ Returns trimmed array with at most max_obs elements. Last element corresponds to current date """

    # Find index of first non-nan value. This is needed for all stocks that are not listed at the beginning of the backtest period
    first_valid_index = np.where(arr == arr[np.isfinite(arr)][0])[0][0]

    available_observations = current_date_index - first_valid_index

    if available_observations >= max_obs:
        arr = arr[current_date_index - max_obs:current_date_index+1]
    else:
        arr = arr[first_valid_index:current_date_index+1]

    return arr
def chaikin_volatility(data: pd.DataFrame, current_date: str, look_back_period: int):
    """ Returns Chaikin volatility """
    current_date_index = np.where(data["Date"].values == current_date)[0][0]
    data_high = trim_stock_data(data["High"].values, current_date_index)
    data_low = trim_stock_data(data["Low"].values, current_date_index)

    smoothed_difference = exponential_moving_average(data_high-data_low,look_back_period)

    cv = (smoothed_difference[look_back_period:]/smoothed_difference[:-look_back_period]-1)*100
    return cv

def volatility_coefficient(data: pd.DataFrame, current_date: str, look_back_period: int = 14) -> float:
    """Computes the volatility coefficient in the specified time frame"""

    current_date_index = np.where(data["Date"].values == current_date)[0][0]
    data_open = trim_stock_data(data["Open"].values,current_date_index, max_obs=look_back_period)

    volatility = np.std(data_open)
    mean = np.mean(data_open)

    if np.isnan(-(volatility / mean)):
        print("test")

    return -(volatility / mean)
def compute_peaks(data: pd.DataFrame, current_date: str, look_back_period: int = 100):
    """Returns array of values of identified peaks"""

    current_date_index = np.where(data["Date"].values == current_date)[0][0]
    data_open = trim_stock_data(data["Open"].values,current_date_index, max_obs=look_back_period)

    peaks,_ = find_peaks(data_open, prominence=5)
    peak_values = data_open[peaks]

    return peak_values