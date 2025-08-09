"""
Dash App Module for Interactive Economy Simulator

Initializes and configures the Dash web application for the Economy Simulator project.

- Sets up the layout and callback logic
- Exposes the WSGI server (`app`) for production (e.g., via Gunicorn)
- Supports local development when run directly
"""

from dash import Dash
from dashboard.src.layout import layout
from dashboard.src.callbacks import register_callbacks

# Initialize Dash app
app = Dash(__name__)
app.title = "Economy Simulator"

# Set layout and callbacks
app.layout = layout
register_callbacks(app)

# Expose the Flask WSGI server for deployment
server = app.server  # For use with Gunicorn and other WSGI servers

# Run development server if executed directly
if __name__ == "__main__":
    app.run(debug=True)
