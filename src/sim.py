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
        volatility_input (float): Volatility sensitivity, controlling the magnitude of random
                      fluctuations in alpha and rho.
        memory_input (int): The size of the historical memory window used for anomaly detection.
        history (Deque[Dict[str, Any]]): A double-ended queue storing the state of the
                                         simulation at each timestep, limited by `memory_input`.
        t (int): The current timestep of the simulation.
    """

    def __init__(
        self,
        volatility_input: float,
        memory_input: int,
        propensities: List[float],
        savings: List[float],
        consumption_init: float = 0.0,
        wages_init: float = 0.0,
    ):
        """
        Initializes a new EconomyNetwork simulation instance.

        Parameters:
            volatility_input (float): A value greater than 0 that defines the volatility sensitivity
                          of the system's parameters (alpha, rho).
            memory_input (int): An integer greater than 1 that defines the size of the
                             history for anomaly detection.
            propensities (List[float]): A list containing two float values: [alpha, rho].
                                Alpha is the household's propensity to consume, rho is the firm's.
                                Both must be in the range [0, 1].
            savings (List[float]): A list containing two float values: [household_savings, firm_savings].
            consumption_init (float): The initial consumption value.
            wages_init (float): The initial wages value.
        """

        # --- Instance Attribute Initialization ---
        self.volatility_input = volatility_input
        self.memory_input = memory_input
        self.t = 0

        # Define the initial state of the simulation
        initial_state = {
            "alpha": propensities[0],
            "rho": propensities[1],
            "outliers": {"alpha": [False], "rho": [False]},
            "savings_households": savings[0],
            "savings_firms": savings[1],
            "consumption": consumption_init,
            "wages": wages_init,
        }

        # Initialize the history deque with the initial state
        self.history: Deque[Dict[str, Any]] = deque([initial_state], maxlen=memory_input)

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
            else max(0.01, min(0.99, prev["alpha"] + random.uniform(-self.volatility_input, self.volatility_input)))
        )
        rho = (
            rho_override
            if rho_override is not None
            else max(0.01, min(0.99, prev["rho"] + random.uniform(-self.volatility_input, self.volatility_input)))
        )

        # --- Economic Model Calculations ---

        factor = (1/alpha * 1/rho - 1) ** -1

        # Calculate consumption based on wages, household savings, and the household factor
        consumption = factor * (1/rho * prev["savings_households"] + prev["savings_firms"])

        # Calculate wages based on savings and the derived factors
        wages = factor * (prev["savings_households"] + 1/alpha * prev["savings_firms"])

        # Update savings based on consumption and wages
        savings_households = (1/alpha - 1) * consumption
        savings_firms = (1/rho - 1) * wages

        # --- Anomaly Detection ---
        # Only run anomaly detection if the history is at its maximum length
        if len(self.history) == self.memory_input:
            alpha_vals = self.get_values("alpha") + [alpha]
            rho_vals = self.get_values("rho") + [rho]
            alpha_out = detect_anomaly(alpha_vals)
            rho_out = detect_anomaly(rho_vals)
            outliers = {
                "alpha": (prev["outliers"]["alpha"] + [alpha_out])[-self.memory_input:],
                "rho": (prev["outliers"]["rho"] + [rho_out])[-self.memory_input:],
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
            now["consumption"] +
            now["wages"] +
            now["savings_households"] +
            now["savings_firms"]
        )

        if total == 0:
            return np.zeros((2, 2))

        return np.array([
            [now["savings_households"] / total, now["consumption"] / total],
            [now["wages"] / total, now["savings_firms"] / total],
        ])
