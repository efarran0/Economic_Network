import numpy as np

class AnomalyDetection:
    def __init__(self, data):
        self.data = data

    def zscore(self, value, threshold=2):
        mean = np.mean(self.data)
        std = np.std(self.data)
        z_score = (value - mean)/std
        return bool((std != 0) and (np.abs(z_score) > threshold))

    def iqr(self, value, factor=1.5):
        q1 = np.percentile(self.data, 25)
        q3 = np.percentile(self.data, 75)
        iqr = q3 - q1
        lower_bound = q1 - factor * iqr
        upper_bound = q3 + factor * iqr
        return bool((value < lower_bound) or (value > upper_bound))
