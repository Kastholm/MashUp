import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/page3")

layout = html.Div(
    [
        html.H2("Page 3", className="mb-4"),
        html.P("Dette er side 3 af dashboardet."),
        dbc.Card(
            [
                dbc.CardBody(
                    [
                        html.H5("Side 3 Indhold", className="card-title"),
                        html.P("Her kan du tilføje dit indhold til side 3."),
                    ]
                )
            ],
            className="mt-4"
        )
    ]
)

