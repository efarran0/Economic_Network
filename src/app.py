"""
Dash App Module for Interactive Economic Simulator.

This module initializes and configures the main Dash web application for the
Economic Simulator project. It sets up the app's core components: the layout and
the callback logic.

The main application instance `app` and the underlying Flask server `server`
are exposed for both local development and production deployment.

Components:
- `app`: The main Dash application instance.
- `server`: The underlying Flask WSGI server for production environments like Gunicorn.
- `layout`: The application's visual structure.
- `register_callbacks`: The function to connect all interactive logic.
"""

# --- Imports ---
# Third-party libraries
from dash import Dash

# Local application modules
from src.layout import layout
from src.callbacks import register_callbacks

# --- App Initialization ---
# Initialize the Dash application with a unique name.
# This name is used to find resources, and can be used for the page title.
app = Dash(__name__)
app.title = "Economic Network"

# --- Layout Assignment ---
# Assign the application's layout, which defines the HTML structure.
# This layout is imported from the src.layout module.
app.layout = layout

# --- Callback Registration ---
# Register all callback functions with the Dash app.
# Callbacks are the core logic that makes the app interactive.
register_callbacks(app)

# --- Deployment Entry Point ---
# Expose the underlying Flask server for production deployment.
# This is the entry point used by web servers like Gunicorn or uWSGI.
server = app.server

# --- Local Development Entry Point ---
# This block runs the app when the file is executed directly.
if __name__ == "__main__":
    # Start the development server in debug mode for live reloading and detailed error messages.
    app.run(debug=True)
