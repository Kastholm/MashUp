import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/")

layout = html.Div(
    [
        html.H2("Home Page", className="mb-4"),
        html.P("Velkommen til MashUp Dashboard!"),
        dbc.Card(
            [
                dbc.CardBody(
                    [
                        html.H5("Dashboard Oversigt", className="card-title"),
                        html.P("Dette er hjemmesiden for dit Dash projekt."),
                    ]
                )
            ],
            className="mt-4"
        )
    ]
)

