"""
Anomaly Detection Module for Interactive Economy Simulator.

This module provides a robust set of functions to detect anomalies within
univariate time series data. It leverages a two-step process: first, it
decomposes the time series to isolate seasonal, trend, and residual components.
Then, it applies the Interquartile Range (IQR) method to the residuals to
identify outliers, which are flagged as anomalies.
"""

# --- Imports ---
# Standard library imports
import math
from typing import Sequence

# Third-party library imports
import numpy as np
import pandas as pd
from statsmodels.tsa.seasonal import seasonal_decompose

# --- Helper Functions ---
def _iqr(residuals: pd.Series, factor: float = 1.5) -> bool:
    """
    Detects whether the latest value in a residual series is an outlier based on the IQR method.

    This function calculates the quartiles (Q1, Q3), determines the IQR, and then defines
    the lower and upper bounds for outliers. The last value of the `residuals` series
    is then checked against these bounds.

    Parameters:
        residuals (pd.Series): A time series of residuals from seasonal decomposition.
        factor (float): The IQR multiplier used to define the outlier thresholds.
                        A common value is 1.5.

    Returns:
        bool: True if the latest residual is an outlier, False otherwise.
    """
    # Calculate the first (Q1) and third (Q3) quartiles of the residual series
    q1 = np.percentile(residuals, 25)
    q3 = np.percentile(residuals, 75)

    # Calculate the Interquartile Range (IQR)
    iqr_range = q3 - q1

    # Define the lower and upper bounds for outliers
    lower_bound = q1 - factor * iqr_range
    upper_bound = q3 + factor * iqr_range

    # Check if the last residual falls outside the defined bounds
    return bool(residuals.iloc[-1] < lower_bound or residuals.iloc[-1] > upper_bound)


# --- Main Functions ---
def detect_anomaly(
    timeseries: Sequence[float],
    model: str = "additive",
    seasonality: float = 0.05,
    iqr_factor: float = 1.5
) -> bool:
    """
    Detects anomalies in a univariate time series using seasonal decomposition and IQR.

    The function first performs a seasonal decomposition of the time series to
    extract the residual component. It then calls the `_iqr` helper function to
    determine if the latest residual is an outlier.

    Parameters:
        timeseries (Sequence[float]): A list or array of floats representing the time series data.
        model (str): The seasonal decomposition model to use. Options are "additive"
                     (default) or "multiplicative".
        seasonality (float): The ratio (0-1) used to estimate the seasonal period.
                             For example, a value of 0.05 means the period is 5% of the series length.
        iqr_factor (float): The IQR multiplier for outlier detection. A higher value
                            makes the detection less sensitive.

    Returns:
        bool: True if an anomaly is detected in the latest residual, False otherwise.

    Raises:
        ValueError: If the input time series is empty or if residuals cannot be computed.
    """
    # Validate that the time series data is not empty
    if not timeseries:
        raise ValueError("Error: The input time series data must not be empty.")

    # Calculate the seasonal period based on the series length and seasonality factor
    n = len(timeseries)
    period = max(2, math.ceil(n * seasonality))

    # Convert the sequence to a pandas Series for decomposition
    series = pd.Series(timeseries, index=pd.RangeIndex(n))

    # Perform seasonal decomposition
    decomposition = seasonal_decompose(
        series, model=model, period=period, extrapolate_trend="freq"
    )

    # Extract residuals and remove any NaN values that may result from decomposition
    residuals = decomposition.resid.dropna()

    # Validate that the residuals were successfully computed
    if residuals.empty:
        raise ValueError("Error: Residuals could not be computed from seasonal decomposition.")

    # Call the helper function to detect if the latest residual is an anomaly
    return _iqr(residuals, factor=iqr_factor)
