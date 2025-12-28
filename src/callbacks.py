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
from src.sim import EconomicNetwork


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
        Output('omegah-output', 'value'),
        Output('omegaf-output', 'value'),
        Input('start_btn', 'n_clicks'),
        Input('stop_btn', 'n_clicks'),
        Input('interval-update', 'n_intervals'),
        Input('omegah-output', 'value'),
        Input('omegaf-output', 'value'),
        State('screen', 'data'),
        State('econ-store', 'data'),
        State('savings_household_input', 'value'),
        State('savings_firm_input', 'value'),
        State('omegah_input', 'value'),
        State('omegaf_input', 'value'),
        State('volatility_input', 'value'),
        State('memory_input', 'value'),
        prevent_initial_call=True,
    )
    def control_and_update(
            start_clicks: int,
            stop_clicks: int,
            n_intervals: int,
            omegah_slider: Optional[float],
            omegaf_slider: Optional[float],
            screen: str,
            econ_data: Optional[str],
            savings_household: float,
            savings_firm: float,
            omegah_input: float,
            omegaf_input: float,
            volatility_input: float,
            memory_input: int,
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
            omegah_slider (Optional[float]): The current value of the omegah slider.
            omegaf_slider (Optional[float]): The current value of the omegaf slider.
            screen (str): The current screen being displayed ('setup' or 'sim').
            econ_data (Optional[str]): A JSON-serialized string of the simulation's history.
            savings_household (float): The value from the household savings input.
            savings_firm (float): The value from the firm savings input.
            omegah_input (float): The value from the initial omegah input field.
            omegaf_input (float): The value from the initial omegaf input field.
            volatility_input (float): The value from the volatility input field.
            memory_input (int): The value from the memory input field.

        Returns:
            Tuple: A tuple containing the updated state for the following outputs:
                   - screen data
                   - serialized economic data
                   - interval disabled flag
                   - heatmap figure
                   - propensity graph figure
                   - omegah slider value
                   - omegaf slider value
        """
        ctx = callback_context
        if not ctx.triggered:
            raise PreventUpdate

        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

        # Handle the start button click
        if trigger_id == 'start_btn':
            # --- Input Validation ---
            inputs = [
                omegah_input,
                omegaf_input,
                savings_household,
                savings_firm,
                volatility_input,
                memory_input
            ]

            if any(v is None for v in inputs):
                raise PreventUpdate

            # Initialize a new EconomicNetwork instance with user-provided parameters
            econ = EconomicNetwork(
                volatility_input,
                memory_input,
                [omegah_input, omegaf_input],
                [savings_household, savings_firm],
            )

            # Serialize and store the initial simulation history
            data = json.dumps(list(econ.history))

            # Transition to the simulation screen and enable periodic updates
            return 'sim', data, False, go.Figure(), go.Figure(), omegah_input, omegaf_input

        # Handle the stop button click
        elif trigger_id == 'stop_btn':
            # Return to the setup screen and disable the interval
            return 'setup', None, True, go.Figure(), go.Figure(), None, None

        # Handle simulation updates or slider changes
        elif trigger_id in {'interval-update', 'omegah-output', 'omegaf-output'} and screen == 'sim':
            if not econ_data:
                raise PreventUpdate

            # Reconstruct the EconomicNetwork instance from the serialized data
            history_list = json.loads(econ_data)
            last_state = history_list[-1]

            # Re-initialize the model with the last known parameters
            econ = EconomicNetwork(
                volatility_input,
                memory_input,
                [last_state["omegah"], last_state["omegaf"]],
                [last_state["savings_household"], last_state["savings_firm"]],
                last_state.get("consumption", 0),
                last_state.get("wage", 0),
            )
            # Restore the full history
            econ.history = deque(history_list, maxlen=memory_input)

            # Determine if a slider override is active
            omegah_override = omegah_slider if trigger_id == 'omegah-output' else None
            omegaf_override = omegaf_slider if trigger_id == 'omegaf-output' else None

            # Advance the simulation by one step
            econ.step(omegah_override=omegah_override, omegaf_override=omegaf_override)

            # Reserialize the updated history
            data = json.dumps(list(econ.history))

            # --- Plot Generation ---
            # Extract data from history for plotting
            t_vals = list(range(-len(econ.history) + 1, 1))
            omegah_vals = [round(s['omegah'], 2) for s in econ.history]
            omegaf_vals = [round(s['omegaf'], 2) for s in econ.history]

            # Extract outlier data for highlighting
            omegah_outliers: List[Any] = econ.history[-1].get('outliers', {}).get('omegah', [])
            omegaf_outliers: List[Any] = econ.history[-1].get('outliers', {}).get('omegaf', [])

            # === Heatmap Figure ===
            matrix = econ.get_matrix()
            labels = np.array([['savings_household', 'consumption'], ['wage', 'savings_firm']])
            fig_heatmap = go.Figure(data=go.Heatmap(
                z=matrix,
                x=['household', 'firm'],
                y=['household', 'firm'],
                colorscale=[[0.0, "#fff59d"], [0.25, "#FAF9F6"], [1.0, "#cba6f7"]],
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
                rows=1, cols=2, column_widths=[0.7, 0.3], horizontal_spacing=0.10
            )

            # Time series plot (left subplot)
            fig_combined.add_trace(go.Scatter(x=t_vals, y=omegah_vals, name='α', mode='lines', hoverinfo='none', showlegend=False),
                                   row=1, col=1)
            fig_combined.add_trace(go.Scatter(x=t_vals, y=omegaf_vals, name='ρ', mode='lines', hoverinfo='none', showlegend=False),
                                   row=1, col=1)
            fig_combined.update_xaxes(
                title_text='Time (t)',
                dtick=1,
                tickvals=t_vals,
                ticktext=[str(v) if v != 0 else "now" for v in t_vals],
                range=[min(t_vals), max(t_vals)],
                showgrid=True,
                gridcolor='lightgrey',
                row=1,
                col=1
            )
            fig_combined.update_yaxes(title_text='Value',
                                      range=[0, 1],
                                      showgrid=True,
                                      gridcolor='lightgrey',
                                      row=1,
                                      col=1)

            # Latest value plot (right subplot)
            fig_combined.add_trace(
                go.Scatter(x=[1] * len(omegah_vals), y=omegah_vals, mode='markers',
                           marker=dict(color='blue', size=5), name='α', hoverinfo='none', showlegend=False),
                row=1, col=2
            )
            fig_combined.add_trace(
                go.Scatter(x=[1.8] * len(omegaf_vals), y=omegaf_vals, mode='markers',
                           marker=dict(color='red', size=5), name='ρ', hoverinfo='none', showlegend=False),
                row=1, col=2
            )
            fig_combined.update_xaxes(
                range=[0.5, 2.5], tickvals=[1, 1.8], ticktext=['α', 'ρ'],
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
            fig_combined.add_shape(type='line', x0=1.8, x1=1.8, y0=0, y1=1,
                                   line=dict(color='red', width=1, dash='dash'),
                                   row=1, col=2)

            # --- Annotation per Outlier ---
            fig_combined.add_annotation(
                x=0.77,
                y=0.95,
                xref='paper',
                yref='paper',
                text="★<br>Outlier",
                showarrow=False,
                align='center',
                font=dict(size=14, color="firebrick"),
                xanchor='right',
                yanchor='top'
            )

            # Highlight outliers with a star marker
            for i, is_out in enumerate(omegah_outliers):
                if is_out:
                    fig_combined.add_trace(
                        go.Scatter(x=[t_vals[i]], y=[omegah_vals[i]], mode='markers',
                                   marker=dict(color='firebrick', size=12, symbol='star'),
                                   hoverinfo='none',
                                   showlegend=False,
                                   cliponaxis=False),
                        row=1, col=1
                    )
            for i, is_out in enumerate(omegaf_outliers):
                if is_out:
                    fig_combined.add_trace(
                        go.Scatter(x=[t_vals[i]], y=[omegaf_vals[i]], mode='markers',
                                   marker=dict(color='firebrick', size=12, symbol='star'),
                                   hoverinfo='none',
                                   showlegend=False,
                                   cliponaxis=False),
                        row=1, col=1
                    )

            fig_combined.update_layout(
                title_text="Historical propensity data",
                title_x=0.45,
                title_y=0.88,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                showlegend=True,
                height=500,
                width=585,
                legend=dict(
                    x=0.75,
                    y=0.95,
                    xanchor='right',
                    yanchor='top',
                    bgcolor='rgba(255,255,255,0.5)',
                    bordercolor='black',
                    borderwidth=1
                )
            )

            return screen, data, False, fig_heatmap, fig_combined, omegah_vals[-1], omegaf_vals[-1]

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
