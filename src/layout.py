"""
Dash Layout Module for Interactive Economy Simulator

This module defines the layout for the Economy Simulator Dash application.

It includes two main screens:
- Setup screen: for inputting initial parameters before starting the simulation.
- Simulation screen: dashboard displaying interactive graphs and controls.

The layout also contains hidden stores and intervals used for managing app state.
"""

from dash import dcc, html

layout = html.Div([
    # Stores for app state management
    dcc.Store(id='econ-store'),                                                         # Store for sim data
    dcc.Store(id='screen', data='setup'),                                               # Track which screen is active
    dcc.Interval(id='interval-update', interval=2000, n_intervals=0, disabled=True),    # Timer updates (2 sec)

    # Setup screen for configuring initial simulation parameters
    html.Div(id='setup-screen', children=[
        html.H1("Economy simulator - Setting"),

        html.Div([
            html.Label("Initial households savings:"),
            dcc.Input(id='s_h_input', type='number', value=100, step=1,
                      style={'display': 'block', 'width': '100%'}),
        ], style={'marginBottom': '15px'}),

        html.Div([
            html.Label("Initial firms savings:"),
            dcc.Input(id='s_f_input', type='number', value=100, step=1,
                      style={'display': 'block', 'width': '100%'}),
        ], style={'marginBottom': '15px'}),

        html.Div([
            html.Label("Initial consumption propensity (α):"),
            dcc.Input(id='alpha_input', type='number', value=0.5, min=0.01, max=0.99, step=0.01,
                      style={'display': 'block', 'width': '100%'}),
        ], style={'marginBottom': '15px'}),

        html.Div([
            html.Label("Initial salary payment propensity (ρ):"),
            dcc.Input(id='rho_input', type='number', value=0.5, min=0.01, max=0.99, step=0.01,
                      style={'display': 'block', 'width': '100%'}),
        ], style={'marginBottom': '15px'}),

        html.Div([
            html.Label("Volatility:"),
            dcc.Input(id='sens_input', type='number', value=0.05, step=0.01,
                      style={'display': 'block', 'width': '100%'}),
        ], style={'marginBottom': '20px'}),

        html.Div([
            html.Label("Memory:"),
            dcc.Input(id='mem_input', type='number', value=30, step=1,
                      style={'display': 'block', 'width': '100%'}),
        ], style={'marginBottom': '20px'}),

        html.Button('Start simulation', id='start_btn', n_clicks=0,
                    style={'display': 'block', 'marginTop': '10px'})
    ], style={'display': 'block', 'maxWidth': '400px', 'margin': 'auto'}),

    # Simulation dashboard screen (initially hidden)
    html.Div(id='sim-screen', children=[
        html.H1("Economy simulator - dashboard"),
        html.Button('Stop and go back', id='stop_btn', n_clicks=0),

        html.Div([

            # Economic matrix graph
            html.Div([
                dcc.Graph(id='matrix-graph', style={'height': '600px', 'width': '100%'}),
            ], style={
                'width': '60%',
                'display': 'inline-block',
                'verticalAlign': 'top'
            }),

            # Controls and propensity graph
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

                # Combined propensity graph
                dcc.Graph(id='propensity-graph', style={'height': '600px', 'width': '100%'}),
            ], style={
                'width': '38%',
                'display': 'inline-block',
                'verticalAlign': 'top',
                'paddingLeft': '2%',
            }),

        ])
    ], style={'display': 'none'})
])
