from dash import Dash
from src.layout import layout
from src.callbacks import register_callbacks

# Initialize Dash app
dash_app = Dash(__name__)
dash_app.title = "Simulació ECONOMY"

# Setup layout and callbacks
dash_app.layout = layout
register_callbacks(dash_app)

# Expose the WSGI application object
server = dash_app.server

# This makes it work with both Gunicorn and direct execution
app = server

# Executar l'aplicació
if __name__ == '__main__':
    app.run(debug=True)
