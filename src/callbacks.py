"""
Callbacks module for the Economic Network Dash application.

This module defines the main callbacks to control the economic simulation,
update the system state, and generate interactive visualizations within the app.

The callbacks handle:
- Simulation start/stop control and screen navigation.
- Periodic updates of the economic data via a hidden `dcc.Interval` component.
- Real-time generation of a heatmap and time-series plot.
- Management of the simulation state, which is stored in a serialized format.
"""

# --- Imports ---
# Standard library imports
import json
from typing import Tuple, List, Optional, Any
from collections import deque

# Third-party library imports
import numpy as np
import plotly.graph_objs as go
from dash import Input, Output, State, callback_context, no_update
from dash.exceptions import PreventUpdate
from plotly.subplots import make_subplots

# Local application imports
from src.sim import EconomyNetwork


def register_callbacks(app) -> None:
    """
    Registers the Dash callbacks to control the simulation and update the UI.

    Parameters:
        app (Dash): The Dash application instance to which callbacks are registered.
    """

    @app.callback(
        Output('screen', 'data'),
        Output('econ-store', 'data'),
        Output('interval-update', 'disabled'),
        Output('matrix-graph', 'figure'),
        Output('propensity-graph', 'figure'),
        Output('alpha-output', 'value'),
        Output('rho-output', 'value'),
        Input('start_btn', 'n_clicks'),
        Input('stop_btn', 'n_clicks'),
        Input('interval-update', 'n_intervals'),
        Input('alpha-output', 'value'),
        Input('rho-output', 'value'),
        State('screen', 'data'),
        State('econ-store', 'data'),
        State('beta_input', 'value'),
        State('delta_input', 'value'),
        State('savings_households_input', 'value'),
        State('savings_firms_input', 'value'),
        State('alpha_input', 'value'),
        State('rho_input', 'value'),
        State('sens_input', 'value'),
        State('mem_input', 'value'),
        prevent_initial_call=True,
    )
    def control_and_update(
            start_clicks: int,
            stop_clicks: int,
            n_intervals: int,
            alpha_slider: Optional[float],
            rho_slider: Optional[float],
            screen: str,
            econ_data: Optional[str],
            beta_input: float,
            delta_input: float,
            savings_households: float,
            savings_firms: float,
            alpha_input: float,
            rho_input: float,
            sens: float,
            mem_input: int,
    ) -> Tuple[str, Optional[str], bool, go.Figure, go.Figure, Optional[float], Optional[float]]:
        """
        Manages the simulation lifecycle and updates the UI based on user interactions and time intervals.

        This callback is the central hub for the application logic. It handles
        the transition between the 'setup' and 'simulation' screens, initializes
        and updates the economic model, and generates the figures for the dashboard.

        Parameters:
            start_clicks (int): Number of clicks on the 'Start simulation' button.
            stop_clicks (int): Number of clicks on the 'Stop and go back' button.
            n_intervals (int): The number of intervals elapsed since the simulation started.
            alpha_slider (Optional[float]): The current value of the alpha slider.
            rho_slider (Optional[float]): The current value of the rho slider.
            screen (str): The current screen being displayed ('setup' or 'sim').
            econ_data (Optional[str]): A JSON-serialized string of the simulation's history.
            beta_input (float): The value from the beta input field.
            delta_input (float): The value from the delta input field.
            savings_households (float): The value from the household savings input.
            savings_firms (float): The value from the firm savings input.
            alpha_input (float): The value from the initial alpha input field.
            rho_input (float): The value from the initial rho input field.
            sens (float): The value from the volatility input field.
            mem_input (int): The value from the memory size input field.

        Returns:
            Tuple: A tuple containing the updated state for the following outputs:
                   - screen data
                   - serialized economic data
                   - interval disabled flag
                   - heatmap figure
                   - propensity graph figure
                   - alpha slider value
                   - rho slider value
        """
        ctx = callback_context
        if not ctx.triggered:
            raise PreventUpdate

        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

        # Handle the start button click
        if trigger_id == 'start_btn':
            # Initialize a new EconomyNetwork instance with user-provided parameters
            econ = EconomyNetwork(
                sens,
                mem_input,
                [beta_input, delta_input],
                [alpha_input, rho_input],
                [savings_households, savings_firms],
            )
            # Serialize the initial history and store it
            data = json.dumps(list(econ.history))
            # Return to switch to the simulation screen and enable the interval
            return 'sim', data, False, go.Figure(), go.Figure(), alpha_input, rho_input

        # Handle the stop button click
        elif trigger_id == 'stop_btn':
            # Return to the setup screen and disable the interval
            return 'setup', None, True, go.Figure(), go.Figure(), None, None

        # Handle simulation updates or slider changes
        elif trigger_id in {'interval-update', 'alpha-output', 'rho-output'} and screen == 'sim':
            if not econ_data:
                raise PreventUpdate

            # Reconstruct the EconomyNetwork instance from the serialized data
            history_list = json.loads(econ_data)
            last_state = history_list[-1]

            # Re-initialize the model with the last known parameters
            econ = EconomyNetwork(
                sens,
                mem_input,
                [last_state["beta"], last_state["delta"]],
                [last_state["alpha"], last_state["rho"]],
                [last_state["savings_households"], last_state["savings_firms"]],
                last_state.get("consumption", 0),
                last_state.get("wages", 0),
            )
            # Restore the full history
            econ.history = deque(history_list, maxlen=mem_input)

            # Determine if a slider override is active
            alpha_override = alpha_slider if trigger_id == 'alpha-output' else None
            rho_override = rho_slider if trigger_id == 'rho-output' else None

            # Advance the simulation by one step
            econ.step(alpha_override=alpha_override, rho_override=rho_override)

            # Reserialize the updated history
            data = json.dumps(list(econ.history))

            # --- Plot Generation ---
            # Extract data from history for plotting
            t_vals = list(range(-len(econ.history) + 1, 1))
            alpha_vals = [round(s['alpha'], 2) for s in econ.history]
            rho_vals = [round(s['rho'], 2) for s in econ.history]

            # Extract outlier data for highlighting
            alpha_outliers: List[Any] = econ.history[-1].get('outliers', {}).get('alpha', [])
            rho_outliers: List[Any] = econ.history[-1].get('outliers', {}).get('rho', [])

            # === Heatmap Figure ===
            matrix = econ.get_matrix()
            labels = np.array([['savings_households', 'consumption'], ['wages', 'savings_firms']])
            fig_heatmap = go.Figure(data=go.Heatmap(
                z=matrix,
                x=['households', 'firms'],
                y=['households', 'firms'],
                colorscale=[[0.0, "#ffcccc"], [0.5, "#ccffff"], [1.0, "#ffcccc"]],
                text=labels,
                texttemplate="%{text}<br>(%{z:.2%})",
                hoverinfo='none',
                textfont={"size": 16, "color": "#4a4a4a"},
                zmin=0,
                zmax=1,
            ))
            fig_heatmap.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            fig_heatmap.update_yaxes(autorange="reversed")

            # === Combined Time Series Figure (Propensity Graph) ===
            fig_combined = make_subplots(
                rows=1, cols=2, column_widths=[0.7, 0.3], horizontal_spacing=0.05
            )

            # Time series plot (left subplot)
            fig_combined.add_trace(go.Scatter(x=t_vals, y=alpha_vals, name='α', mode='lines', hoverinfo='none'),
                                   row=1, col=1)
            fig_combined.add_trace(go.Scatter(x=t_vals, y=rho_vals, name='ρ', mode='lines', hoverinfo='none'),
                                   row=1, col=1)
            fig_combined.update_xaxes(
                title_text='Time (t)',
                dtick=1,
                tickvals=t_vals,
                ticktext=[str(v) if v != 0 else "now" for v in t_vals],
                range=[min(t_vals), max(t_vals)],
                row=1, col=1
            )
            fig_combined.update_yaxes(title_text='Value', range=[0, 1], row=1, col=1)

            # Latest value plot (right subplot)
            fig_combined.add_trace(
                go.Scatter(x=[1] * len(alpha_vals), y=alpha_vals, mode='markers',
                           marker=dict(color='blue', size=5), name='α'), row=1, col=2
            )
            fig_combined.add_trace(
                go.Scatter(x=[2] * len(rho_vals), y=rho_vals, mode='markers',
                           marker=dict(color='red', size=5), name='ρ'), row=1, col=2
            )
            fig_combined.update_xaxes(
                range=[0.5, 2.5], tickvals=[1, 2], ticktext=['α', 'ρ'],
                showgrid=False, zeroline=False, showticklabels=True, row=1, col=2
            )
            fig_combined.update_yaxes(
                title_text='', range=[0, 1],
                showgrid=False, showticklabels=False, row=1, col=2
            )

            # Add reference lines and hidden legend entry for outliers
            fig_combined.add_shape(type='line', x0=1, x1=1, y0=0, y1=1,
                                   line=dict(color='blue', width=1, dash='dash'),
                                   row=1, col=2)
            fig_combined.add_shape(type='line', x0=2, x1=2, y0=0, y1=1,
                                   line=dict(color='red', width=1, dash='dash'),
                                   row=1, col=2)
            fig_combined.add_trace(
                go.Scatter(x=[None], y=[None], mode='markers',
                           marker=dict(color='firebrick', size=12, symbol='star'),
                           name='Outlier'),
                row=1, col=1
            )

            # Highlight outliers with a star marker
            for i, is_out in enumerate(alpha_outliers):
                if is_out:
                    fig_combined.add_trace(
                        go.Scatter(x=[t_vals[i]], y=[alpha_vals[i]], mode='markers',
                                   marker=dict(color='firebrick', size=12, symbol='star'),
                                   hoverinfo='none',
                                   showlegend=False),
                        row=1, col=1
                    )
            for i, is_out in enumerate(rho_outliers):
                if is_out:
                    fig_combined.add_trace(
                        go.Scatter(x=[t_vals[i]], y=[rho_vals[i]], mode='markers',
                                   marker=dict(color='firebrick', size=12, symbol='star'),
                                   hoverinfo='none',
                                   showlegend=False),
                        row=1, col=1
                    )

            fig_combined.update_layout(
                title_text="Historical propensity data",
                title_x=0.5,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                showlegend=True,
                height=500
            )

            return screen, data, False, fig_heatmap, fig_combined, alpha_vals[-1], rho_vals[-1]

        else:
            raise PreventUpdate

    @app.callback(
        Output('setup-screen', 'style'),
        Output('sim-screen', 'style'),
        Input('screen', 'data')
    )
    def toggle_screens(screen: str) -> Tuple[dict, dict]:
        """
        Toggles the visibility of the setup and simulation screens.

        This callback ensures that only one of the main screens is visible at any given time.

        Parameters:
            screen (str): The current screen identifier ('setup' or 'sim').

        Returns:
            Tuple: A tuple of two dictionaries, containing the style properties
                   for the setup and simulation screens, respectively.
        """
        if screen == 'setup':
            return {'display': 'block'}, {'display': 'none'}
        elif screen == 'sim':
            return {'display': 'none'}, {'display': 'block'}
        else:
            return no_update, no_update
