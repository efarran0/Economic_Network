import pandas as pd
import numpy as np
import math
from statsmodels.tsa.seasonal import seasonal_decompose


def iqr(residuals: pd.Series, factor: float =1.5) -> bool:
    q1 = np.percentile(residuals, 25)
    q3 = np.percentile(residuals, 75)
    iqr_range = q3 - q1
    lower_bound = q1 - factor * iqr_range
    upper_bound = q3 + factor * iqr_range
    value = residuals.iloc[-1]
    return bool((value < lower_bound) or (value > upper_bound))

def tsa(timeseries: list[float], model: str ="additive", seasonality: float =0.05) -> bool:
    n = len(timeseries)
    series = pd.Series(timeseries,
                       index=pd.RangeIndex(n))
    period = max(2, math.ceil(n * seasonality))
    result = seasonal_decompose(series,
                                model=model,
                                period=period,
                                extrapolate_trend="freq")
    residuals = result.resid.dropna()
    return iqr(residuals)