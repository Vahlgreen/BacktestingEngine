import pandas as pd
import numpy as np

import functions

def rsi(data: pd.DataFrame, current_date: str, look_back_period: int = 14) -> bool:
    """Source: https://en.wikipedia.org/wiki/Relative_strength_index"""

    current_date_index = np.where(data["Date"].values == current_date)[0][0]
    data_close = functions.trim_stock_data(data["Close"].values, current_date_index)

    if data_close.size < look_back_period:
        return False

    diff_arr = np.diff(data_close,1)

    # arrays containing gains and losses
    gain_arr = np.where(diff_arr > 0, diff_arr, 0)
    loss_arr = np.abs(np.where(diff_arr < 0, diff_arr, 0))

    average_gain = functions.exponential_moving_average(gain_arr, look_back_period)
    average_loss = functions.exponential_moving_average(loss_arr, look_back_period)

    with np.errstate(divide='ignore'):
        current_rsi = 100 - (100 / (1 + average_gain / average_loss))[-1]
    return 30 < current_rsi < 70
def bollinger_bands(data: pd.DataFrame, current_date: str, look_back_period: int = 14, d: int = 2) -> bool:
    """Source: https://en.wikipedia.org/wiki/Bollinger_Bands"""

    current_date_index = np.where(data["Date"].values == current_date)[0][0]
    data_close = functions.trim_stock_data(data["Close"].values, current_date_index)

    if data_close.size < look_back_period:
        return False

    smoothed_data_close = functions.exponential_moving_average(data_close, look_back_period)

    # Compute rolling standard deviation
    n_rows = data_close.size - look_back_period + 1
    n = data_close.strides[0]
    a2D = np.lib.stride_tricks.as_strided(data_close, shape=(n_rows, look_back_period), strides=(n, n))
    rolling_std = np.std(a2D, axis=1)

    upper_band = smoothed_data_close[-1] + d * rolling_std[-1]
    lower_band = smoothed_data_close[-1] - d * rolling_std[-1]

    percent_b = (data_close[-1] - lower_band) / (upper_band - lower_band)*100

    return percent_b > 75
def moving_average(data: pd.DataFrame, current_date: str, long_window_size: int = 14, short_window_size: int = 7) -> bool:
    """Computes average price in the given window ranges"""

    current_date_index = np.where(data["Date"].values == current_date)[0][0]
    data_close = functions.trim_stock_data(data["Close"].values, current_date_index)

    if data_close.size < 10:
        return False

    long_window_average = np.mean(data_close[-long_window_size:])
    short_window_average = np.mean(data_close[-short_window_size:])

    return long_window_average < short_window_average
def dmi_(data: pd.DataFrame,current_date: str, look_back_period: int = 14) -> bool:
    """Source: https://en.wikipedia.org/wiki/Average_directional_movement_index"""

    current_date_index = np.where(data["Date"].values == current_date)[0][0]
    data_high = functions.trim_stock_data(data["High"].values, current_date_index)
    data_low = functions.trim_stock_data(data["Low"].values, current_date_index)
    data_close = functions.trim_stock_data(data["Close"].values, current_date_index)

    if data_close.size < look_back_period:
        return False

    hl = data_high-data_low
    hc = np.abs(functions.shifted_array_difference(data_high, data_close, 2))
    lc = np.abs(functions.shifted_array_difference(data_low, data_close, 2))
    tr = np.nanmax(np.column_stack((hc, hl, lc)),axis=1)

    atr = functions.exponential_moving_average(tr, look_back_period)
    hph = functions.shifted_array_difference(data_high, data_high, 2)
    pll = functions.shifted_array_difference(data_low, data_low, 1)

    pdx = np.where((hph>pll) & (hph>0), hph, 0)
    mdx = np.where((hph<pll) & (pll>0), pll, 0)

    spdm = functions.exponential_moving_average(pdx, look_back_period)
    smdm = functions.exponential_moving_average(mdx, look_back_period)

    pdmi = (spdm/atr)*100
    mdmi = (smdm/atr)*100

    dx = (np.abs(pdmi - mdmi) / (pdmi + mdmi)) * 100

    adx = functions.exponential_moving_average(dx[np.logical_not(np.isnan(dx))], look_back_period)
    return adx[-1] > 50
def chaikin_volatility(data: pd.DataFrame, current_date: str, look_back_period: int = 14) -> bool:
    """Source: https://www.marketvolume.com/technicalanalysis/chaikinvolatility.asp"""

    current_date_index = np.where(data["Date"].values == current_date)[0][0]
    data_high = functions.trim_stock_data(data["High"].values, current_date_index)
    data_low = functions.trim_stock_data(data["Low"].values, current_date_index)

    if data_high.size <= look_back_period:
        return False

    smoothed_difference = functions.exponential_moving_average(data_high - data_low, look_back_period)

    cv = (smoothed_difference[look_back_period:]/smoothed_difference[:-look_back_period]-1)*100

    current_cv = cv[-1]

    return current_cv < 50
