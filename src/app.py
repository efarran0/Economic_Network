"""
Dash App Module for Interactive Economy Simulator

This module initializes and configures the Dash web application
for the Economy Simulator project.

It sets up the app layout and registers callbacks, then exposes
the WSGI server for deployment (e.g., with Gunicorn). When run
directly, it starts the development server.
"""

from dash import Dash
from src.layout import layout
from src.callbacks import register_callbacks

# Initialize the Dash app
dash_app = Dash(__name__)
dash_app.title = "Economy simulator"  # Browser tab title

# Assign the app layout (imported from src.layout)
dash_app.layout = layout

# Register interaction callbacks (imported from src.callbacks)
register_callbacks(dash_app)

# Expose the Flask WSGI server for deployment platforms like Gunicorn
server = dash_app.server

# Alias for convenience — both Gunicorn and direct execution use this
app = server

# Run the development server when executing this file directly
if __name__ == '__main__':
    app.run(debug=True)
