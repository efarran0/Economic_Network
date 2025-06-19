import json
import numpy as np
from dash import Input, Output, State, callback_context, no_update
from dash.exceptions import PreventUpdate
import plotly.graph_objs as go
from src.sim import EconomyNetwork

def register_callbacks(app):

    @app.callback(
        Output('screen', 'data'),
        Output('econ-store', 'data'),
        Output('interval-update', 'disabled'),
        Output('matrix-graph', 'figure'),
        Output('propensions-graph', 'figure'),
        Output('alpha-output', 'value'),
        Output('ro-output', 'value'),
        Input('start_btn', 'n_clicks'),
        Input('stop_btn', 'n_clicks'),
        Input('interval-update', 'n_intervals'),
        Input('s_h_input', 'value'),
        Input('s_f_input', 'value'),
        Input('alpha_input', 'value'),
        Input('ro_input', 'value'),
        Input('sens_input', 'value'),
        State('screen', 'data'),
        State('econ-store', 'data'),
        prevent_initial_call=True
    )
    def control_and_update(start_clicks, stop_clicks, n_intervals,
                           s_h, s_f, alpha, ro, sens,
                           screen, econ_data):

        ctx = callback_context
        if not ctx.triggered:
            raise PreventUpdate

        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if trigger_id == 'start_btn':
            econ = EconomyNetwork([s_h, s_f], [alpha, ro], sens)
            data = json.dumps(econ.sys)
            empty_fig = go.Figure()
            return 'sim', data, False, empty_fig, empty_fig, alpha, ro

        elif trigger_id == 'stop_btn':
            return 'setup', no_update, True, no_update, no_update, no_update, no_update

        elif screen == 'sim':
            if not econ_data:
                raise PreventUpdate

            sys = json.loads(econ_data)
            econ = EconomyNetwork([0, 0], [0.5, 0.5], 0.05)
            econ.sys = {int(k): v for k, v in sys.items()}

            # Apply updated slider values dynamically
            econ.update_params([s_h, s_f], [alpha, ro], sens)

            econ.step()

            t = [x - max(econ.sys.keys()) for x in econ.sys.keys()]
            alpha_vals = [v['alpha'] for v in econ.sys.values()]
            ro_vals = [v['ro'] for v in econ.sys.values()]

            t = t[-5:]
            alpha_vals = [round(x, 2) for x in alpha_vals][-5:]
            ro_vals = [round(x, 2) for x in ro_vals][-5:]

            matrix = econ.get_matrix()
            labels = np.array([
                ['s_h', 'c'],
                ['w', 's_f']
            ])

            fig1 = go.Figure(data=go.Heatmap(
                z=matrix,
                x=['houses', 'firms'],
                y=['houses', 'firms'],
                colorscale=[
                    [0.0, "#d4a373"],
                    [0.5, "#e6b566"],
                    [1.0, "#fbeec1"]
                ],
                text=labels,
                texttemplate="%{text}",
                textfont={"size": 16, "color": "red"},
                zmin=0,
                zmax=1
            ))
            fig1.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            fig1.update_yaxes(autorange="reversed")

            fig2 = go.Figure([
                go.Scatter(x=t, y=alpha_vals, name='α', mode='lines'),
                go.Scatter(x=t, y=ro_vals, name='ρ', mode='lines')
            ])
            fig2.update_layout(
                title='Propensions α i ρ',
                xaxis_title='t',
                yaxis_title='Valor',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(
                    dtick=1,
                    tickmode='array',
                    tickvals=t,
                    ticktext=[v if v != 0 else "now" for v in t]
                ),
                yaxis=dict(range=[0, 1])
            )

            return screen, json.dumps(econ.sys), False, fig1, fig2, alpha_vals[-1], ro_vals[-1]

        else:
            raise PreventUpdate

    @app.callback(
        Output('setup-screen', 'style'),
        Output('sim-screen', 'style'),
        Input('screen', 'data')
    )
    def toggle_screens(screen):
        if screen == 'setup':
            return {'display': 'block'}, {'display': 'none'}
        elif screen == 'sim':
            return {'display': 'none'}, {'display': 'block'}
        else:
            return no_update, no_update
