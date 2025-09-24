"""
Dash Layout Module for Interactive Economy Network.

This module defines the visual structure (layout) of the Dash application.
It separates the user interface into two main sections: a setup screen for
initial parameter input and a simulation dashboard for displaying real-time
results.

It also includes hidden components like `dcc.Store` and `dcc.Interval` that
are essential for managing the application's state and triggering simulation
updates via callbacks.
"""

# --- Imports ---
from dash import dcc, html

# --- Layout Definition ---
# The main layout is a single Div that contains all the application's components.
layout = html.Div(
    [
        # --- Hidden Stores for State Management ---
        # These components do not render anything on the screen but are crucial
        # for storing data and state that needs to be shared between callbacks.
        dcc.Store(
            id='econ-store',
            data=None,  # This will store the serialized EconomyNetwork object.
        ),
        dcc.Store(
            id='screen',
            data='setup',  # Controls which screen ('setup' or 'sim') is visible.
        ),
        dcc.Interval(
            id='interval-update',
            interval=2000,  # Interval in milliseconds (2s)
            n_intervals=0,
            disabled=True,  # Disabled by default until the simulation starts.
        ),

        # === Setup Screen: Input initial parameters before simulation starts ===
        html.Div(
            id='setup-screen',
            children=[
                html.H1("Economy Network - Setup"),
                html.P("Adjust the initial economic network parameters."),

                # --- Initial propensities (alpha and rho) ---
                html.Div([
                    html.Label("Initial consumption propensity (α):", style={'fontWeight': 'bold'}),
                    dcc.Input(
                        id='alpha_input',
                        type='number',
                        placeholder='Format: %.2f',
                        value=0.50,
                        min=0.01,
                        max=0.99,
                        step=0.01,
                        style={'display': 'block', 'width': '100%'}
                    ),
                ], style={'marginBottom': '15px'}),

                html.Div([
                    html.Label("Initial salary payment propensity (ρ):", style={'fontWeight': 'bold'}),
                    dcc.Input(
                        id='rho_input',
                        type='number',
                        placeholder='Format: %.2f',
                        value=0.50,
                        min=0.01,
                        max=0.99,
                        step=0.01,
                        style={'display': 'block', 'width': '100%'}
                    ),
                ], style={'marginBottom': '15px'}),

                # --- Initial savings inputs ---
                html.Div([
                    html.Label("Initial households savings:", style={'fontWeight': 'bold'}),
                    dcc.Input(
                        id='savings_households_input',
                        type='number',
                        placeholder='Format: %d',
                        value=100,
                        step=1,
                        min=0,
                        style={'display': 'block', 'width': '100%'}
                    ),
                ], style={'marginBottom': '15px'}),

                html.Div([
                    html.Label("Initial firms savings:", style={'fontWeight': 'bold'}),
                    dcc.Input(
                        id='savings_firms_input',
                        type='number',
                        placeholder='Format: %d',
                        value=0,
                        step=1,
                        min=0,
                        style={'display': 'block', 'width': '100%'}
                    ),
                ], style={'marginBottom': '15px'}),

                # --- Volatility and memory inputs ---
                html.Div([
                    html.Label("Volatility:", style={'fontWeight': 'bold'}),
                    dcc.Input(
                        id='volatility_input',
                        type='number',
                        placeholder='Format: %.2f',
                        value=0.05,
                        step=0.01,
                        min=0.01,
                        style={'display': 'block', 'width': '100%'}
                    ),
                ], style={'marginBottom': '20px'}),

                html.Div([
                    html.Label("Memory:", style={'fontWeight': 'bold'}),
                    dcc.Input(
                        id='memory_input',
                        type='number',
                        placeholder='Format: %d',
                        value=5,
                        step=1,
                        min=3,
                        style={'display': 'block', 'width': '100%'}
                    ),
                ], style={'marginBottom': '20px'}),

                # --- Start simulation button ---
                html.Button(
                    'Start simulation',
                    id='start_btn',
                    n_clicks=0,
                    style={'display': 'block', 'marginTop': '10px'}
                )
            ],
            style={'display': 'block', 'maxWidth': '400px', 'margin': 'auto'}
        ),

        # === Simulation Dashboard Screen: Hidden by default ===
        html.Div(
            id='sim-screen',
            children=[
                html.H1("Economy Network - Dashboard"),
                html.Button('Stop and go back', id='stop_btn', n_clicks=0),

                html.Div([
                    # Economic matrix graph (left side)
                    html.Div(
                        [dcc.Graph(id='matrix-graph',
                                   style={'height': '600px', 'width': '100%'},
                                   config={'displayModeBar': False})],
                        style={'width': '60%', 'display': 'inline-block', 'verticalAlign': 'top'}
                    ),

                    # Controls and propensity graph (right side)
                    html.Div(
                        [
                            html.Label("α (editable):", style={'fontWeight': 'bold'}),
                            dcc.Slider(
                                id='alpha-output',
                                min=0.01,
                                max=0.99,
                                step=0.01,
                                value=0.5,
                                marks={0.01: '0.01', 0.99: '0.99'},
                                tooltip={"always_visible": True, "placement": "bottom"},
                                className='danger-gradient-slider'
                            ),
                            html.Label("ρ (editable):", style={'fontWeight': 'bold'}),
                            dcc.Slider(
                                id='rho-output',
                                min=0.01,
                                max=0.99,
                                step=0.01,
                                value=0.5,
                                marks={0.01: '0.01', 0.99: '0.99'},
                                tooltip={"always_visible": True, "placement": "bottom"},
                                className='danger-gradient-slider'
                            ),
                            dcc.Graph(id='propensity-graph',
                                      style={'height': '600px', 'width': '100%'},
                                      config={'displayModeBar': False}),
                        ],
                        style={'width': '38%', 'display': 'inline-block', 'verticalAlign': 'top', 'paddingLeft': '2%'}
                    ),
                ])
            ],
            style={'display': 'none'}  # Hidden initially
        ),
    ]
)
