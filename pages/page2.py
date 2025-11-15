import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/page2")

layout = html.Div(
    [
        html.H2("Page 2", className="mb-4"),
        html.P("Dette er side 2 af dashboardet."),
        dbc.Card(
            [
                dbc.CardBody(
                    [
                        html.H5("Side 2 Indhold", className="card-title"),
                        html.P("Her kan du tilføje dit indhold til side 2."),
                    ]
                )
            ],
            className="mt-4"
        )
    ]
)

