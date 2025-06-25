from dash import dcc, html

layout = html.Div([
    # Stores i control d'estat
    dcc.Store(id='econ-store'),
    dcc.Store(id='screen', data='setup'),
    dcc.Interval(id='interval-update', interval=2000, n_intervals=0, disabled=True),

    # Pantalla de configuració
    html.Div(id='setup-screen', children=[
        html.H1("Economy simulator - Setting"),

        html.Div([
            html.Label("Initial households savings:"),
            dcc.Input(id='s_h_input', type='number', value=100, step=1, style={'display': 'block', 'width': '100%'}),
        ], style={'marginBottom': '15px'}),

        html.Div([
            html.Label("Initial firms savings:"),
            dcc.Input(id='s_f_input', type='number', value=100, step=1, style={'display': 'block', 'width': '100%'}),
        ], style={'marginBottom': '15px'}),

        html.Div([
            html.Label("Initial consumption propensity (α):"),
            dcc.Input(id='alpha_input', type='number', value=0.5, min=0.01, max=0.99, step=0.01, style={'display': 'block', 'width': '100%'}),
        ], style={'marginBottom': '15px'}),

        html.Div([
            html.Label("Initial salary payment propensity (ρ):"),
            dcc.Input(id='rho_input', type='number', value=0.5, min=0.01, max=0.99, step=0.01, style={'display': 'block', 'width': '100%'}),
        ], style={'marginBottom': '15px'}),

        html.Div([
            html.Label("Volatility:"),
            dcc.Input(id='sens_input', type='number', value=0.05, step=0.01, style={'display': 'block', 'width': '100%'}),
        ], style={'marginBottom': '20px'}),

        html.Div([
            html.Label("Memory:"),
            dcc.Input(id='mem_input', type='number', value=5, step=1, style={'display': 'block', 'width': '100%'}),
        ], style={'marginBottom': '20px'}),

        html.Button('Start simulation', id='start_btn', n_clicks=0, style={'display': 'block', 'marginTop': '10px'})
    ], style={'display': 'block', 'maxWidth': '400px', 'margin': 'auto'}),

    # Pantalla de simulació
    html.Div(id='sim-screen', children=[
        html.H1("Economy simulator - dashboard"),
        html.Button('Stop and go back', id='stop_btn', n_clicks=0),

        html.Div([

            # Gràfic de matriu econòmica
            html.Div([
                dcc.Graph(id='matrix-graph', style={'height': '600px', 'width': '100%'}),
            ], style={
                'width': '60%',
                'display': 'inline-block',
                'verticalAlign': 'top'
            }),

            # Controls i gràfic de propensions
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
                    id='rho-output', min=0.01, max=0.99, step=0.01, value=0.5,
                    marks=None,
                    tooltip={"always_visible": True, "placement": "bottom"},
                    className='danger-gradient-slider'
                ),

                # Gràfic combinat
                dcc.Graph(id='propensions-graph', style={'height': '600px', 'width': '100%'}),
            ], style={
                'width': '38%',
                'display': 'inline-block',
                'verticalAlign': 'top',
                'paddingLeft': '2%',
            }),

        ])
    ], style={'display': 'none'})
])
