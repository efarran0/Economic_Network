"""
Anomaly Detection Module for Interactive Economy Simulator

This module provides functions to detect anomalies in time series data
using seasonal decomposition and the Interquartile Range (IQR) method.
"""

import pandas as pd
import numpy as np
import math
from statsmodels.tsa.seasonal import seasonal_decompose

def iqr(residuals: pd.Series, factor: float = 1.5) -> bool:
    """
    Detects whether the last value in the residuals series is an outlier based on the Interquartile Range (IQR) method.

    Parameters:
    -----------
    residuals : pd.Series
        A pandas Series of residual values from a time series decomposition.
    factor : float, optional (default=1.5)
        The multiplier for the IQR to define the lower and upper bounds for outlier detection.

    Returns:
    --------
    bool
        Whether the last value in residuals is an outlier.
    """
    q1 = np.percentile(residuals, 25)
    q3 = np.percentile(residuals, 75)
    iqr_range = q3 - q1
    lower_bound = q1 - factor * iqr_range
    upper_bound = q3 + factor * iqr_range
    value = residuals.iloc[-1]
    return bool((value < lower_bound) or (value > upper_bound))


def tsa(timeseries: list[float], model: str = "additive", seasonality: float = 0.05) -> bool:
    """
    Performs seasonal decomposition of a time series and detects anomalies in the residuals using the IQR method.

    Parameters:
    -----------
    timeseries : list of float
        The time series data to analyze.
    model : str, optional (default="additive")
        The type of seasonal decomposition model to use. Options are 'additive' or 'multiplicative'.
    seasonality : float, optional (default=0.05)
        The estimated seasonality ratio (between 0 and 1) to determine the period of decomposition.

    Returns:
    --------
    bool
        Whether an anomaly is detected in the residuals.
    """
    n = len(timeseries)
    series = pd.Series(timeseries, index=pd.RangeIndex(n))
    period = max(2, math.ceil(n * seasonality))
    result = seasonal_decompose(series,
                                model=model,
                                period=period,
                                extrapolate_trend="freq")
    residuals = result.resid.dropna()
    return iqr(residuals)
