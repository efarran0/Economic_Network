"""
Dash Callback Module for Interactive Economy Simulation

This module registers callbacks for a Dash web app simulating an economic network.
Features:
- Start/stop simulation control
- Dynamic state updates with intervals
- Heatmap visualization of system matrix
- Dual-axis time series plot of economic parameters (alpha and rho)
- Anomaly/outlier detection and display

Dependencies:
- Dash, Plotly, NumPy
- EconomyNetwork class from dashboard.src.sim
"""

import json
import numpy as np
from typing import Tuple, Union
from dash import Input, Output, State, callback_context, no_update
from dash.exceptions import PreventUpdate
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from dashboard.src.sim import EconomyNetwork


def register_callbacks(app):
    """
    Register Dash callbacks to control simulation and update UI elements.

    Parameters:
        app (Dash): Dash app instance.
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
        State('s_h_input', 'value'),
        State('s_f_input', 'value'),
        State('alpha_input', 'value'),
        State('rho_input', 'value'),
        State('sens_input', 'value'),
        State('mem_input', 'value'),
        prevent_initial_call=True
    )
    def control_and_update(
        start_clicks: int,
        stop_clicks: int,
        n_intervals: int,
        alpha_slider: float,
        rho_slider: float,
        screen: str,
        econ_data: Union[str, None],
        s_h: float,
        s_f: float,
        alpha_input: float,
        rho_input: float,
        sens: float,
        mem_input: int
    ) -> Tuple[str, Union[str, None], bool, go.Figure, go.Figure, float, float]:
        """
        Controls simulation lifecycle and updates UI elements accordingly.

        Returns updated screen, serialized system state, interval enabled flag,
        heatmap figure, time series figure, and current alpha/rho values.
        """
        ctx = callback_context
        if not ctx.triggered:
            raise PreventUpdate

        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if trigger_id == 'start_btn':
            econ = EconomyNetwork([s_h, s_f], [alpha_input, rho_input], sens, mem_input)
            data = json.dumps(econ.sys)
            empty_fig = go.Figure()
            return 'sim', data, False, empty_fig, empty_fig, alpha_input, rho_input

        elif trigger_id == 'stop_btn':
            return 'setup', no_update, True, no_update, no_update, no_update, no_update

        elif trigger_id in {'interval-update', 'alpha-output', 'rho-output'} and screen == 'sim':
            if not econ_data:
                raise PreventUpdate

            sys = json.loads(econ_data)
            econ = EconomyNetwork([0, 0], [0.5, 0.5], sens, mem_input)
            econ.sys = {int(k): v for k, v in sys.items()}

            alpha_override = alpha_slider if trigger_id == 'alpha-output' else None
            rho_override = rho_slider if trigger_id == 'rho-output' else None

            econ.step(alpha_override=alpha_override, rho_override=rho_override)

            t = max(econ.sys.keys())
            if alpha_override is not None:
                econ.sys[t]['alpha'] = alpha_override
            if rho_override is not None:
                econ.sys[t]['rho'] = rho_override

            t_vals = [x - t for x in econ.sys.keys()]
            alpha_vals = [round(v['alpha'], 2) for v in econ.sys.values()]
            rho_vals = [round(v['rho'], 2) for v in econ.sys.values()]
            t_plot = t_vals[-mem_input:]
            alpha_plot = alpha_vals[-mem_input:]
            rho_plot = rho_vals[-mem_input:]

            # Heatmap figure
            matrix = econ.get_matrix()
            labels = np.array([['s_h', 'c'], ['w', 's_f']])
            fig_heatmap = go.Figure(data=go.Heatmap(
                z=matrix,
                x=['households', 'firms'],
                y=['households', 'firms'],
                colorscale=[[0.0, "#d4a373"], [0.5, "#e6b566"], [1.0, "#fbeec1"]],
                text=labels,
                texttemplate="%{text}",
                hovertemplate="%{z}<extra></extra>",
                textfont={"size": 16, "color": "red"},
                zmin=0,
                zmax=1
            ))
            fig_heatmap.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            fig_heatmap.update_yaxes(autorange="reversed")

            # Combined time series plot
            fig_combined = make_subplots(rows=1, cols=2, column_widths=[0.7, 0.3], horizontal_spacing=0.05)

            fig_combined.add_trace(go.Scatter(x=t_plot, y=alpha_plot, name='α', mode='lines'), row=1, col=1)
            fig_combined.add_trace(go.Scatter(x=t_plot, y=rho_plot, name='ρ', mode='lines'), row=1, col=1)

            fig_combined.update_xaxes(
                title_text='t',
                dtick=1,
                tickvals=t_plot,
                ticktext=[str("") if v != 0 else "now" for v in t_plot],
                range=[min(t_plot), max(t_plot)],
                row=1, col=1
            )
            fig_combined.update_yaxes(title_text='Value', range=[0, 1], row=1, col=1)

            # Markers on right plot
            fig_combined.add_trace(
                go.Scatter(x=[1]*len(alpha_plot), y=alpha_plot, mode='markers',
                           marker=dict(color='blue', size=5), name='α'), row=1, col=2)
            fig_combined.add_trace(
                go.Scatter(x=[2]*len(rho_plot), y=rho_plot, mode='markers',
                           marker=dict(color='red', size=5), name='ρ'), row=1, col=2)

            fig_combined.update_xaxes(
                range=[0.5, 2.5], tickvals=[1, 2], ticktext=['α', 'ρ'],
                showgrid=False, zeroline=False, showticklabels=True, row=1, col=2
            )
            fig_combined.update_yaxes(
                title_text='', range=[0, 1],
                showgrid=False, showticklabels=False, row=1, col=2
            )

            # Reference lines
            fig_combined.add_shape(type='line', x0=1, x1=1, y0=0, y1=1,
                                   line=dict(color='blue', width=1, dash='dash'), row=1, col=2)
            fig_combined.add_shape(type='line', x0=2, x1=2, y0=0, y1=1,
                                   line=dict(color='red', width=1, dash='dash'), row=1, col=2)

            # Outlier legend symbol (hidden)
            fig_combined.add_trace(
                go.Scatter(x=[None], y=[None], mode='markers',
                           marker=dict(color='firebrick', size=12, symbol='star'),
                           name='Outlier'), row=1, col=1
            )

            # Highlight outliers
            alpha_outliers = econ.sys[t]['outliers']['alpha']
            rho_outliers = econ.sys[t]['outliers']['rho']

            for i, is_out in enumerate(alpha_outliers):
                if is_out:
                    fig_combined.add_trace(
                        go.Scatter(x=[t_plot[i]], y=[alpha_plot[i]], mode='markers',
                                   marker=dict(color='firebrick', size=12, symbol='star'),
                                   showlegend=False), row=1, col=1)
                    fig_combined.add_trace(
                        go.Scatter(x=[1], y=[alpha_plot[i]], mode='markers',
                                   marker=dict(color='firebrick', size=12, symbol='star'),
                                   showlegend=False), row=1, col=2)

            for i, is_out in enumerate(rho_outliers):
                if is_out:
                    fig_combined.add_trace(
                        go.Scatter(x=[t_plot[i]], y=[rho_plot[i]], mode='markers',
                                   marker=dict(color='firebrick', size=12, symbol='star'),
                                   showlegend=False), row=1, col=1)
                    fig_combined.add_trace(
                        go.Scatter(x=[2], y=[rho_plot[i]], mode='markers',
                                   marker=dict(color='firebrick', size=12, symbol='star'),
                                   showlegend=False), row=1, col=2)

            fig_combined.update_layout(
                title_text="Historical propensity data",
                title_x=0.5,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                showlegend=True,
                height=500
            )
            # Hide legend for duplicate traces
            fig_combined['data'][2]['showlegend'] = False
            fig_combined['data'][3]['showlegend'] = False

            return screen, json.dumps(econ.sys), False, fig_heatmap, fig_combined, alpha_vals[-1], rho_vals[-1]

        else:
            raise PreventUpdate

    @app.callback(
        Output('setup-screen', 'style'),
        Output('sim-screen', 'style'),
        Input('screen', 'data')
    )
    def toggle_screens(screen: str) -> Tuple[dict, dict]:
        """
        Toggle visibility of setup and simulation screens based on current screen state.

        Args:
            screen (str): Current screen identifier ('setup' or 'sim').

        Returns:
            Tuple of two dicts for style properties of setup and sim screens.
        """
        if screen == 'setup':
            return {'display': 'block'}, {'display': 'none'}
        elif screen == 'sim':
            return {'display': 'none'}, {'display': 'block'}
        else:
            return no_update, no_update
