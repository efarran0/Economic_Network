"""
Anomaly Detection Module for Interactive Economy Simulator

This module provides functions to detect anomalies in time series data
using seasonal decomposition and the Interquartile Range (IQR) method.
"""

import math
import numpy as np
import pandas as pd
from typing import Sequence
from statsmodels.tsa.seasonal import seasonal_decompose


def iqr(residuals: pd.Series, factor: float = 1.5) -> bool:
    """
    Detects whether the latest value in a residual series is an outlier based on the IQR method.

    Parameters:
        residuals (pd.Series): Series of residuals from time series decomposition.
        factor (float): IQR multiplier to define outlier thresholds. Default is 1.5.

    Returns:
        bool: True if the last residual is an outlier, False otherwise.
    """
    q1 = np.percentile(residuals, 25)
    q3 = np.percentile(residuals, 75)
    iqr_range = q3 - q1
    lower = q1 - factor * iqr_range
    upper = q3 + factor * iqr_range
    return residuals.iloc[-1] < lower or residuals.iloc[-1] > upper


def detect_anomaly(
    timeseries: Sequence[float],
    model: str = "additive",
    seasonality: float = 0.05,
    iqr_factor: float = 1.5
) -> bool:
    """
    Detects anomalies in a univariate time series using seasonal decomposition and IQR.

    Parameters:
        timeseries (Sequence[float]): Input time series data (e.g., list or array of floats).
        model (str): Seasonal decomposition model; "additive" or "multiplicative". Default is "additive".
        seasonality (float): Ratio (0–1) to estimate the seasonal period. Default is 0.05.
        iqr_factor (float): IQR multiplier for outlier detection. Default is 1.5.

    Returns:
        bool: True if an anomaly is detected in the latest residual, False otherwise.
    """
    if not timeseries:
        raise ValueError("Time series data must not be empty.")

    n = len(timeseries)
    period = max(2, math.ceil(n * seasonality))

    series = pd.Series(timeseries, index=pd.RangeIndex(n))
    decomposition = seasonal_decompose(
        series, model=model, period=period, extrapolate_trend="freq"
    )
    residuals = decomposition.resid.dropna()

    if residuals.empty:
        raise ValueError("Residuals could not be computed from decomposition.")

    return iqr(residuals, factor=iqr_factor)
