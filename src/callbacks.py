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
        prevent_initial_call=True
    )
    def control_and_update(start_clicks, stop_clicks, n_intervals, alpha_slider, rho_slider,
                           screen, econ_data, s_h, s_f, alpha_input, rho_input, sens):

        ctx = callback_context
        if not ctx.triggered:
            raise PreventUpdate

        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if trigger_id == 'start_btn':
            econ = EconomyNetwork([s_h, s_f], [alpha_input, rho_input], sens)
            data = json.dumps(econ.sys)
            empty_fig = go.Figure()
            return 'sim', data, False, empty_fig, empty_fig, alpha_input, rho_input

        elif trigger_id == 'stop_btn':
            return 'setup', no_update, True, no_update, no_update, no_update, no_update

        elif trigger_id in ['interval-update', 'alpha-output', 'rho-output'] and screen == 'sim':
            if not econ_data:
                raise PreventUpdate

            sys = json.loads(econ_data)
            econ = EconomyNetwork([0, 0], [0.5, 0.5], sens)
            econ.sys = {int(k): v for k, v in sys.items()}

            # Determinar overrides des dels sliders
            alpha_override = alpha_slider if trigger_id == 'alpha-output' else None
            rho_override = rho_slider if trigger_id == 'rho-output' else None

            # Aplicar valors als últims estats si l'usuari ha modificat sliders
            t = max(econ.sys.keys())
            if alpha_override is not None:
                econ.sys[t]['alpha'] = alpha_override
            if rho_override is not None:
                econ.sys[t]['rho'] = rho_override

            # Executar següent pas
            econ.step(alpha_override=alpha_override, rho_override=rho_override)

            # Preparar dades per les gràfiques
            t_vals = [x - max(econ.sys.keys()) for x in econ.sys.keys()]
            alpha_vals = [round(v['alpha'], 2) for v in econ.sys.values()]
            rho_vals = [round(v['rho'], 2) for v in econ.sys.values()]

            t_plot = t_vals[-5:]
            alpha_plot = alpha_vals[-5:]
            rho_plot = rho_vals[-5:]

            matrix = econ.get_matrix()
            labels = np.array([['s_h', 'c'], ['w', 's_f']])
            fig1 = go.Figure(data=go.Heatmap(
                z=matrix,
                x=['households', 'firms'],
                y=['households', 'firms'],
                colorscale=[[0.0, "#d4a373"], [0.5, "#e6b566"], [1.0, "#fbeec1"]],
                text=labels,
                texttemplate="%{text}",
                textfont={"size": 16, "color": "red"},
                zmin=0,
                zmax=1
            ))
            fig1.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            fig1.update_yaxes(autorange="reversed")

            fig2 = go.Figure([
                go.Scatter(x=t_plot, y=alpha_plot, name='α', mode='lines'),
                go.Scatter(x=t_plot, y=rho_plot, name='ρ', mode='lines')
            ])
            fig2.update_layout(
                title='Historical propensity data',
                xaxis_title='t',
                yaxis_title='Valor',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(dtick=1, tickvals=t_plot,
                           ticktext=[str(v) if v != 0 else "now" for v in t_plot]),
                yaxis=dict(range=[0, 1])
            )

            return screen, json.dumps(econ.sys), False, fig1, fig2, alpha_vals[-1], rho_vals[-1]

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
