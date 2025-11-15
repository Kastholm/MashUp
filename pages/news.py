import dash
from dash import html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import requests
import os
from dotenv import load_dotenv

load_dotenv()

dash.register_page(__name__, path="/news", name="News")

layout = html.Div(
    [
        html.H2("News - New York Times", className="mb-4"),
        html.P("Henter de seneste nyheder fra New York Times."),
        dbc.Button("Hent Nyheder", id="fetch-news-btn", color="primary", className="mb-3"),
        html.Div(id="news-content")
    ]
)

@callback(
    Output("news-content", "children"),
    Input("fetch-news-btn", "n_clicks"),
    prevent_initial_call=True
)
def fetch_news(n_clicks):
    """Henter nyheder fra New York Times API"""
    try:
        # Hent API key fra environment variable
        api_key = os.getenv("NYT_API_KEY", "your-api-key-here")
        
        # New York Times Top Stories API
        url = f"https://api.nytimes.com/svc/topstories/v2/home.json?api-key={api_key}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            articles = data.get("results", [])[:10]  # Første 10 artikler
            
            cards = []
            for article in articles:
                card = dbc.Card(
                    [
                        dbc.CardBody(
                            [
                                html.H5(article.get("title", "No title"), className="card-title"),
                                html.P(article.get("abstract", "No abstract"), className="card-text"),
                                html.Small(article.get("byline", ""), className="text-muted"),
                                html.Br(),
                                html.A("Læs mere", href=article.get("url", "#"), target="_blank", className="btn btn-sm btn-primary mt-2")
                            ]
                        )
                    ],
                    className="mb-3"
                )
                cards.append(card)
            
            return cards
        else:
            return dbc.Alert(f"Fejl ved hentning af nyheder: {response.status_code}", color="danger")
    except Exception as e:
        return dbc.Alert(f"Fejl: {str(e)}", color="danger")

