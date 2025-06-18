from dash import Dash
from layout import layout
from callbacks import register_callbacks

# Crear l'aplicació Dash
app = Dash(__name__)
app.title = "Simulació ECONOMY"

# Assignar layout i callbacks
app.layout = layout
register_callbacks(app)

# Executar l'aplicació
if __name__ == '__main__':
    app.run(debug=True)
