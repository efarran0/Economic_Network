"""
Dash Sim Module for Interactive Economy Simulator.

This module provides the `EconomyNetwork` class, which simulates a dynamic
economic system. It models the interactions between households and firms,
tracking key parameters like alpha, rho, savings, consumption, and wages.

The simulation is designed to be stepped forward one timestep at a time,
allowing for its seamless integration with a Dash-based user interface.
"""

# --- Imports ---
# Standard library imports
import random
from collections import deque
from typing import Deque, List, Dict, Any, Optional

# Third-party library imports
import numpy as np

# Local application imports
from src.anomaly_detection import detect_anomaly


class EconomyNetwork:
    """
    Simulates a dynamic economic network with evolving parameters and anomaly detection.

    The simulation maintains a history of its state, allowing for the detection of
    outliers in key economic indicators. It uses a simple model to update
    consumption, wages, and savings based on propensity and discount factors.

    Attributes:
        sens (float): Volatility sensitivity, controlling the magnitude of random
                      fluctuations in alpha and rho.
        mem_input (int): The size of the historical memory window used for anomaly detection.
        history (Deque[Dict[str, Any]]): A double-ended queue storing the state of the
                                         simulation at each timestep, limited by `mem_input`.
        t (int): The current timestep of the simulation.
    """

    def __init__(
        self,
        sens: float,
        mem_input: int,
        discounts: List[float],
        prop: List[float],
        savings: List[float],
        consumption_init: float = 0.0,
        wages_init: float = 0.0,
    ):
        """
        Initializes a new EconomyNetwork simulation instance.

        Parameters:
            sens (float): A value greater than 0 that defines the volatility sensitivity
                          of the system's parameters (alpha, rho).
            mem_input (int): An integer greater than 1 that defines the size of the
                             history for anomaly detection.
            discounts (List[float]): A list containing two float values: [beta, delta].
                                     Beta is the household discount factor, delta is the firm's.
            prop (List[float]): A list containing two float values: [alpha, rho].
                                Alpha is the household's propensity to consume, rho is the firm's.
                                Both must be in the range [0, 1].
            savings (List[float]): A list containing two float values: [household_savings, firm_savings].
            consumption_init (float): The initial consumption value.
            wages_init (float): The initial wages value.

        Raises:
            ValueError: If any of the input parameters are outside their valid ranges.
        """
        # --- Parameter Validation ---
        if sens <= 0:
            raise ValueError("Parameter 'sens' (sensitivity) must be a positive number.")
        if mem_input < 2:
            raise ValueError("Parameter 'mem_input' (memory size) must be at least 2.")
        if not all(0 <= p <= 1 for p in prop):
            raise ValueError("Parameters 'alpha' and 'rho' must be in the range [0, 1].")

        # --- Instance Attribute Initialization ---
        self.sens = sens
        self.mem_input = mem_input
        self.t = 0

        # Define the initial state of the simulation
        initial_state = {
            "beta": discounts[0],
            "delta": discounts[1],
            "alpha": prop[0],
            "rho": prop[1],
            "outliers": {"alpha": [False], "rho": [False]},
            "savings_households": savings[0],
            "savings_firms": savings[1],
            "consumption": consumption_init,
            "wages": wages_init,
        }

        # Initialize the history deque with the initial state
        self.history: Deque[Dict[str, Any]] = deque([initial_state], maxlen=mem_input)

    def get_values(self, key: str) -> List[float]:
        """
        Retrieves a list of recent values for a specified key from the simulation history.

        Parameters:
            key (str): The state key (e.g., 'alpha', 'rho', 'consumption') for which
                       to retrieve historical data.

        Returns:
            List[float]: A list of float values from the history for the given key.
        """
        return [state[key] for state in self.history]

    def step(self, alpha_override: Optional[float] = None, rho_override: Optional[float] = None) -> None:
        """
        Advances the simulation by one timestep.

        This method updates the simulation's state, including the parameters alpha and rho,
        consumption, wages, and savings. It also performs anomaly detection on the
        updated parameters if the history is sufficiently long.

        Parameters:
            alpha_override (Optional[float]): An optional float value to manually set the
                                               new alpha for this timestep. Must be in [0, 1].
            rho_override (Optional[float]): An optional float value to manually set the
                                             new rho for this timestep. Must be in [0, 1].
        """
        prev = self.history[-1]

        # Update alpha and rho with random volatility, or use an override value
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

        # --- Economic Model Calculations ---
        try:
            # Household and firm factors are derived from alpha, rho, and discount factors
            household_factor = (1 / alpha - 1) / (1 - prev["beta"])
            firm_factor = (1 / rho - 1) / (1 - prev["delta"])

            # Calculate wages based on savings and the derived factors
            wages = (
                ((1 + household_factor) * (1 + firm_factor) - 1) ** -1
                * ((1 + firm_factor) ** -1 * prev["savings_firms"] + prev["savings_households"])
                + (1 + firm_factor) ** -1 * prev["savings_firms"]
            )
            # Calculate consumption based on wages, household savings, and the household factor
            consumption = (1 + household_factor) ** -1 * (wages + prev["savings_households"])

        except ZeroDivisionError:
            # Handle cases where factors might lead to division by zero,
            # keeping the previous values as a fallback.
            wages, consumption = prev["wages"], prev["consumption"]

        # Update savings based on consumption and wages
        savings_households = prev["savings_households"] + wages - consumption
        savings_firms = prev["savings_firms"] + consumption - wages

        # --- Anomaly Detection ---
        # Only run anomaly detection if the history is at its maximum length
        if len(self.history) == self.mem_input:
            alpha_vals = self.get_values("alpha") + [alpha]
            rho_vals = self.get_values("rho") + [rho]
            alpha_out = detect_anomaly(alpha_vals)
            rho_out = detect_anomaly(rho_vals)
            outliers = {
                "alpha": (prev["outliers"]["alpha"] + [alpha_out])[-self.mem_input:],
                "rho": (prev["outliers"]["rho"] + [rho_out])[-self.mem_input:],
            }
        else:
            # If history is not yet full, initialize outliers as False
            outliers = {
                "alpha": prev["outliers"]["alpha"] + [False],
                "rho": prev["outliers"]["rho"] + [False],
            }

        # --- State Update ---
        self.t += 1
        state = {
            "beta": prev["beta"],
            "delta": prev["delta"],
            "alpha": alpha,
            "rho": rho,
            "outliers": outliers,
            "savings_households": savings_households,
            "savings_firms": savings_firms,
            "consumption": consumption,
            "wages": wages,
        }

        # Add the new state to the history
        self.history.append(state)

    def get_matrix(self) -> np.ndarray:
        """
        Returns a normalized 2x2 matrix representing the current economic state.

        The matrix maps the flow of value between households and firms.
        Matrix structure:
            [[savings_households, consumption],
             [wages,              savings_firms]]

        Returns:
            np.ndarray: A 2x2 NumPy array with normalized values. If the total
                        value is zero, it returns a zero matrix.
        """
        now = self.history[-1]
        total = (
            now["consumption"]
            + now["wages"]
            + now["savings_households"]
            + now["savings_firms"]
        )

        if total == 0:
            return np.zeros((2, 2))

        return np.array([
            [now["savings_households"] / total, now["consumption"] / total],
            [now["wages"] / total, now["savings_firms"] / total],
        ])
