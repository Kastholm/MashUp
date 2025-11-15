import dash
from dash import html, dcc, page_container
import dash_bootstrap_components as dbc
from utils.chuck_norris import create_chuck_norris_banner

# Initialize the Dash app with Bootstrap theme
app = dash.Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)

# Import pages to register them (must be after app instantiation)
from pages import home, news, music, movies, books

# Sidebar navigation
sidebar = dbc.Nav(
    [
        dbc.NavLink("Home", href="/", active="exact"),
        dbc.NavLink("News", href="/news", active="exact"),
        dbc.NavLink("Music", href="/music", active="exact"),
        dbc.NavLink("Movies", href="/movies", active="exact"),
        dbc.NavLink("Books", href="/books", active="exact"),
    ],
    vertical=True,
    pills=True,
    className="bg-light",
    style={"height": "100vh", "padding": "20px"}
)

# Main layout
app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(sidebar, width=2, className="p-0"),
                dbc.Col(
                    [
                        html.H1("MashUp Dashboard", className="mb-4"),
                        create_chuck_norris_banner(),
                        page_container
                    ],
                    width=10,
                    style={"padding": "20px"}
                ),
            ],
            className="g-0"
        )
    ],
    fluid=True,
    className="p-0"
)

if __name__ == "__main__":
    app.run(debug=True)

