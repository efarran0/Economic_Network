from dash import Dash
from src.layout import layout
from src.callbacks import register_callbacks

# Crear l'aplicació Dash
app = Dash(__name__)
app.title = "Simulació ECONOMY"

# Assignar layout i callbacks
app.layout = layout
register_callbacks(app)

server= app.server

# Executar l'aplicació
if __name__ == '__main__':
    app.run(debug=True)
