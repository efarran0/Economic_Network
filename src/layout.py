from dash import dcc, html

layout = html.Div([
    # Stores i control d'estat
    dcc.Store(id='econ-store'),
    dcc.Store(id='screen', data='setup'),
    dcc.Interval(id='interval-update', interval=2000, n_intervals=0, disabled=True),

    # Pantalla de configuració
    html.Div(id='setup-screen', children=[
        html.H1("Simulador ECONOMY - Configuració Inicial"),

        html.Label("Estalvi inicial Llars:"),
        dcc.Input(id='s_h_input', type='number', value=100, step=1),

        html.Label("Estalvi inicial Empreses:"),
        dcc.Input(id='s_f_input', type='number', value=100, step=1),

        html.Label("Propensió inicial α:"),
        dcc.Input(id='alpha_input', type='number', value=0.5, min=0.01, max=0.99, step=0.01),

        html.Label("Propensió inicial ρ:"),
        dcc.Input(id='ro_input', type='number', value=0.5, min=0.01, max=0.99, step=0.01),

        html.Label("Sensibilitat de canvis:"),
        dcc.Input(id='sens_input', type='number', value=0.05, step=0.01),

        html.Br(),
        html.Button('Iniciar simulació', id='start_btn', n_clicks=0)
    ], style={'display': 'block'}),

    # Pantalla de simulació
    html.Div(id='sim-screen', children=[
        html.H1("Simulació en curs"),
        html.Button('Atura i torna enrere', id='stop_btn', n_clicks=0),

        html.Div([
            html.Div([
                dcc.Graph(id='matrix-graph', style={'height': '600px'})
            ], style={'width': '60%', 'display': 'inline-block'}),

            html.Div([
                html.Label("α (editable):"),
                dcc.Slider(
                    id='alpha-output', min=0.01, max=0.99, step=0.01, value=0.5,
                    marks=None,
                    tooltip={"always_visible": True, "placement": "bottom"},
                    className='danger-gradient-slider'
                ),

                html.Label("ρ (editable):"),
                dcc.Slider(
                    id='ro-output', min=0.01, max=0.99, step=0.01, value=0.5,
                    marks=None,
                    tooltip={"always_visible": True, "placement": "bottom"},
                    className='danger-gradient-slider'
                ),

                dcc.Graph(id='propensions-graph', style={'height': '400px'})
            ], style={
                'width': '38%',
                'display': 'inline-block',
                'paddingLeft': '2%',
                'verticalAlign': 'top'
            })
        ])
    ], style={'display': 'none'})
])
