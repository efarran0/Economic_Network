"""
Dash Sim Module for Interactive Economy Simulator

This module defines the EconomyNetwork class, which simulates an economic system
with dynamic parameters including consumption propensity (alpha), salary payment
propensity (rho), and savings for households and firms. The simulation updates
these parameters over time with controlled volatility and applies anomaly detection
using time series seasonal decomposition.

Key features:
- Dynamic update of economic parameters with stochastic volatility.
- Detection of anomalies in parameter evolution using seasonal decomposition and IQR.
- Generation of a normalized economic matrix representing the current system state.
"""

import random
import numpy as np
from src.anomaly_detection import tsa

class EconomyNetwork:
    """
    A class to simulate an economic network with dynamic parameters and anomaly detection.

    Attributes:
    -----------
    sens : float
        Sensitivity parameter controlling the volatility of alpha and rho changes.
    mem_input : int
        The memory window size used for anomaly detection and storing historical states.
    sys : dict
        A dictionary storing the state of the system at each timestep.

    Methods:
    --------
    get_values(key)
        Retrieves the historical values of a given state key for the memory window.
    step(alpha_override=None, rho_override=None)
        Advances the simulation by one timestep, optionally overriding alpha and rho.
        Calculates new economic variables and detects anomalies using the tsa function.
    get_matrix()
        Returns a normalized 2x2 matrix representing the current economic state.
    """

    def __init__(self, savings, prop, sens, mem_input):
        """
        Initialize the EconomyNetwork with initial parameters.

        Parameters:
        -----------
        savings : list of float
            Initial savings for households and firms [s_h, s_f].
        prop : list of float
            Initial propensity parameters [alpha, rho].
        sens : float
            Sensitivity controlling volatility in alpha and rho.
        mem_input : int
            Memory size used for anomaly detection and tracking states.
        """
        self.sens = sens
        self.mem_input = mem_input
        self.sys = {
            0: {
                "alpha": prop[0],
                "rho": prop[1],
                "outliers": {
                    "alpha": [False],
                    "rho": [False]
                },
                "c": 0,
                "w": 0,
                "s_h": savings[0],
                "s_f": savings[1]
            }
        }

    def get_values(self, key):
        """
        Retrieve a list of historical values for a given state key,
        limited by the memory size.

        Parameters:
        -----------
        key : str
            The key of the value to retrieve (e.g., 'alpha', 'rho').

        Returns:
        --------
        list
            List of values for the specified key from the last mem_input-1 timesteps.
        """
        return [state[key] for t, state in sorted(self.sys.items())[-(self.mem_input - 1):]]

    def step(self, alpha_override=None, rho_override=None):
        """
        Advance the simulation by one timestep, updating state variables.

        Parameters:
        -----------
        alpha_override : float or None, optional
            If provided, overrides the computed alpha value for this step.
        rho_override : float or None, optional
            If provided, overrides the computed rho value for this step.

        The method:
        - Computes alpha and rho with volatility around previous values unless overridden.
        - Calculates consumption (c) and wages (w) using the model equations.
        - Updates household and firm savings.
        - Performs anomaly detection on alpha and rho using tsa() if enough data exists.
        - Saves the new state in self.sys.
        """
        t = max(self.sys.keys())
        prev = self.sys[t]

        # Calculate alpha with optional override and volatility bounds
        alpha = (
            alpha_override
            if alpha_override is not None
            else max(0.01, min(0.99, prev["alpha"] + random.uniform(-self.sens, self.sens)))
        )

        # Calculate rho with optional override and volatility bounds
        rho = (
            rho_override
            if rho_override is not None
            else max(0.01, min(0.99, prev["rho"] + random.uniform(-self.sens, self.sens)))
        )

        try:
            c = (1 / alpha - rho) ** (-1) * (rho * prev["s_f"] + prev["s_h"])
            w = (1 / rho - alpha) ** (-1) * (alpha * prev["s_h"] + prev["s_f"])
        except ZeroDivisionError:
            # If division by zero occurs, keep previous values
            c = prev["c"]
            w = prev["w"]

        s_h = prev["s_h"] + w - c
        s_f = prev["s_f"] + c - w

        # Anomaly detection on alpha and rho values if enough history exists
        if len(self.sys) >= self.mem_input:
            alpha_vals = self.get_values('alpha') + [alpha]
            rho_vals = self.get_values('rho') + [rho]
            alpha_is_out = tsa(alpha_vals)
            rho_is_out = tsa(rho_vals)
            outliers = {
                'alpha': (prev['outliers']['alpha'] + [alpha_is_out])[-self.mem_input:],
                'rho': (prev['outliers']['rho'] + [rho_is_out])[-self.mem_input:]
            }
        else:
            # Not enough data: no outliers detected
            outliers = {
                'alpha': [False] * (len(self.sys) + 1),
                'rho': [False] * (len(self.sys) + 1)
            }

        # Save updated state
        self.sys[t + 1] = {
            "alpha": alpha,
            "rho": rho,
            "outliers": outliers,
            "c": c,
            "w": w,
            "s_h": s_h,
            "s_f": s_f
        }

    def get_matrix(self):
        """
        Compute and return the current normalized economic matrix.

        Returns:
        --------
        np.ndarray
            A 2x2 numpy array with normalized values of household savings, consumption,
            wages, and firm savings.

            Matrix format:
            [[s_h_norm, c_norm],
             [w_norm, s_f_norm]]

        If the total sum of components is zero, returns a zero matrix.
        """
        t = max(self.sys.keys())
        now = self.sys[t]
        n = now["c"] + now["w"] + now["s_h"] + now["s_f"]

        if n == 0:
            return np.zeros((2, 2))

        c_nrm = now["c"] / n
        w_nrm = now["w"] / n
        s_h_nrm = now["s_h"] / n
        s_f_nrm = now["s_f"] / n

        return np.array([
            [s_h_nrm, c_nrm],
            [w_nrm, s_f_nrm]
        ])
