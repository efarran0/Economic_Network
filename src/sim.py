"""
Dash Sim Module for Interactive Economic Simulator.

This module provides the `EconomicNetwork` class, which simulates a dynamic
economic system. It models the interactions between households and firms,
tracking key parameters like omegah, omegaf, savings, consumption, and wages.

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


class EconomicNetwork:
    """
    Simulates a dynamic economic network with evolving parameters and anomaly detection.

    The simulation maintains a history of its state, allowing for the detection of
    outliers in key economic indicators. It uses a simple model to update
    consumption, wages, and savings based on propensity and discount factors.

    Attributes:
        volatility_input (float): Volatility sensitivity, controlling the magnitude of random
                      fluctuations in omegah and omegaf.
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
        Initializes a new EconomicNetwork simulation instance.

        Parameters:
            volatility_input (float): A value greater than 0 that defines the volatility sensitivity
                          of the system's parameters (omegah, omegaf).
            memory_input (int): An integer greater than 1 that defines the size of the
                             history for anomaly detection.
            propensities (List[float]): A list containing two float values: [omegah, omegaf].
                                omegah is the household's propensity to consume, omegaf is the firm's.
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
            "omegah": propensities[0],
            "omegaf": propensities[1],
            "outliers": {"omegah": [False], "omegaf": [False]},
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
            key (str): The state key (e.g., 'omegah', 'omegaf', 'consumption') for which
                       to retrieve historical data.

        Returns:
            List[float]: A list of float values from the history for the given key.
        """
        return [state[key] for state in self.history]

    def step(self, omegah_override: Optional[float] = None, omegaf_override: Optional[float] = None) -> None:
        """
        Advances the simulation by one timestep.

        This method updates the simulation's state, including the parameters omegah and omegaf,
        consumption, wages, and savings. It also performs anomaly detection on the
        updated parameters if the history is sufficiently long.

        Parameters:
            omegah_override (Optional[float]): An optional float value to manually set the
                                               new omegah for this timestep. Must be in [0, 1].
            omegaf_override (Optional[float]): An optional float value to manually set the
                                             new omegaf for this timestep. Must be in [0, 1].
        """
        prev = self.history[-1]

        # Update omegah and omegaf with random volatility, or use an override value
        omegah = (
            omegah_override
            if omegah_override is not None
            else max(0.01, min(0.99, prev["omegah"] + random.uniform(-self.volatility_input, self.volatility_input)))
        )
        omegaf = (
            omegaf_override
            if omegaf_override is not None
            else max(0.01, min(0.99, prev["omegaf"] + random.uniform(-self.volatility_input, self.volatility_input)))
        )

        # --- Economic Model Calculations ---

        factor = (1/omegah * 1/omegaf - 1) ** -1

        # Calculate consumption based on wages, household savings, and the household factor
        consumption = factor * (1/omegaf * prev["savings_households"] + prev["savings_firms"])

        # Calculate wages based on savings and the derived factors
        wages = factor * (prev["savings_households"] + 1/omegah * prev["savings_firms"])

        # Update savings based on consumption and wages
        savings_households = (1/omegah - 1) * consumption
        savings_firms = (1/omegaf - 1) * wages

        # --- Anomaly Detection ---
        # Only run anomaly detection if the history is at its maximum length
        if len(self.history) == self.memory_input:
            omegah_vals = self.get_values("omegah") + [omegah]
            omegaf_vals = self.get_values("omegaf") + [omegaf]
            omegah_out = detect_anomaly(omegah_vals)
            omegaf_out = detect_anomaly(omegaf_vals)
            outliers = {
                "omegah": (prev["outliers"]["omegah"] + [omegah_out])[-self.memory_input:],
                "omegaf": (prev["outliers"]["omegaf"] + [omegaf_out])[-self.memory_input:],
            }
        else:
            # If history is not yet full, initialize outliers as False
            outliers = {
                "omegah": prev["outliers"]["omegah"] + [False],
                "omegaf": prev["outliers"]["omegaf"] + [False],
            }

        # --- State Update ---
        self.t += 1
        state = {
            "omegah": omegah,
            "omegaf": omegaf,
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
