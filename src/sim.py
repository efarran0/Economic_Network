"""
Dash Sim Module for Interactive Economy Simulator

Defines EconomyNetwork class to simulate an economic system with dynamic
parameters (alpha, rho), savings, volatility, and anomaly detection using TSA.
"""

import random
import numpy as np
from dashboard.src.anomaly_detection import tsa


class EconomyNetwork:
    """
    Simulate an economic network with dynamic parameters and anomaly detection.

    Attributes:
        sens (float): Volatility sensitivity for alpha and rho updates.
        mem_input (int): Memory size for anomaly detection and history.
        sys (dict): Stores system state per timestep.
    """

    def __init__(self, savings, prop, sens, mem_input):
        """
        Initialize with initial savings, propensity, sensitivity, and memory.

        Args:
            savings (list[float]): Initial savings [s_h, s_f].
            prop (list[float]): Initial propensities [alpha, rho].
            sens (float): Volatility sensitivity.
            mem_input (int): Memory window for anomaly detection.
        """
        self.sens = sens
        self.mem_input = mem_input
        self.sys = {
            0: {
                "alpha": prop[0],
                "rho": prop[1],
                "outliers": {"alpha": [False], "rho": [False]},
                "c": 0,
                "w": 0,
                "s_h": savings[0],
                "s_f": savings[1]
            }
        }

    def get_values(self, key):
        """
        Get historical values for a given key limited by memory size.

        Args:
            key (str): State key ('alpha', 'rho', etc.).

        Returns:
            list: List of historical values.
        """
        return [state[key] for _, state in sorted(self.sys.items())[-(self.mem_input - 1):]]

    def step(self, alpha_override=None, rho_override=None):
        """
        Advance simulation one step with optional overrides for alpha and rho.

        Updates consumption (c), wages (w), savings (s_h, s_f), and detects anomalies.

        Args:
            alpha_override (float | None): Optional override for alpha.
            rho_override (float | None): Optional override for rho.
        """
        t = max(self.sys.keys())
        prev = self.sys[t]

        # Update alpha and rho with volatility bounds and optional override
        alpha = (
            alpha_override
            if alpha_override is not None
            else max(0.01, min(0.99, prev["alpha"] + random.uniform(-self.sens, self.sens)))
        )
        rho = (
            rho_override
            if rho_override is not None
            else max(0.01, min(0.99, prev["rho"] + random.uniform(-self.sens, self.sens)))
        )

        # Calculate consumption and wages with safe division
        try:
            c = (1 / alpha - rho) ** -1 * (rho * prev["s_f"] + prev["s_h"])
            w = (1 / rho - alpha) ** -1 * (alpha * prev["s_h"] + prev["s_f"])
        except ZeroDivisionError:
            c, w = prev["c"], prev["w"]

        s_h = prev["s_h"] + w - c
        s_f = prev["s_f"] + c - w

        # Anomaly detection if enough history exists
        if len(self.sys) >= self.mem_input:
            alpha_vals = self.get_values("alpha") + [alpha]
            rho_vals = self.get_values("rho") + [rho]
            alpha_out = tsa(alpha_vals)
            rho_out = tsa(rho_vals)
            outliers = {
                "alpha": (prev["outliers"]["alpha"] + [alpha_out])[-self.mem_input:],
                "rho": (prev["outliers"]["rho"] + [rho_out])[-self.mem_input:]
            }
        else:
            outliers = {
                "alpha": [False] * (len(self.sys) + 1),
                "rho": [False] * (len(self.sys) + 1),
            }

        # Save updated state
        self.sys[t + 1] = {
            "alpha": alpha,
            "rho": rho,
            "outliers": outliers,
            "c": c,
            "w": w,
            "s_h": s_h,
            "s_f": s_f,
        }

    def get_matrix(self):
        """
        Return the normalized 2x2 economic matrix for the current state.

        Returns:
            np.ndarray: Normalized matrix [[s_h, c], [w, s_f]].
        """
        t = max(self.sys.keys())
        now = self.sys[t]
        total = now["c"] + now["w"] + now["s_h"] + now["s_f"]

        if total == 0:
            return np.zeros((2, 2))

        return np.array([
            [now["s_h"] / total, now["c"] / total],
            [now["w"] / total, now["s_f"] / total]
        ])
