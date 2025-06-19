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
        dcc.Slider(id='s_h_input', min=0, max=500, step=1, value=100,
                   tooltip={"always_visible": True}, marks=None),

        html.Label("Estalvi inicial Empreses:"),
        dcc.Slider(id='s_f_input', min=0, max=500, step=1, value=100,
                   tooltip={"always_visible": True}, marks=None),

        html.Label("Propensió inicial α:"),
        dcc.Slider(id='alpha_input', min=0.01, max=0.99, step=0.01, value=0.5,
                   tooltip={"always_visible": True}, marks=None),

        html.Label("Propensió inicial ρ:"),
        dcc.Slider(id='ro_input', min=0.01, max=0.99, step=0.01, value=0.5,
                   tooltip={"always_visible": True}, marks=None),

        html.Label("Sensibilitat de canvis:"),
        dcc.Slider(id='sens_input', min=0.01, max=0.2, step=0.01, value=0.05,
                   tooltip={"always_visible": True}, marks=None),

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
                html.Label("α (now):"),
                dcc.Slider(
                    id='alpha-output', min=0, max=1, step=0.01, value=0.5,
                    disabled=True, marks=None,
                    tooltip={"always_visible": True, "placement": "bottom"},
                    className='danger-gradient-slider'
                ),
                html.Label("ρ (now):"),
                dcc.Slider(
                    id='ro-output', min=0, max=1, step=0.01, value=0.5,
                    disabled=True, marks=None,
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
