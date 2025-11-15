import dash
from dash import html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import requests
import os
from dotenv import load_dotenv

load_dotenv()

dash.register_page(__name__, path="/movies", name="Movies")

layout = html.Div(
    [
        html.H2("Movies - Trakt.tv", className="mb-4"),
        html.P("Henter film fra Trakt.tv API."),
        dbc.Button("Hent Populære Film", id="fetch-movies-btn", color="primary", className="mb-3"),
        html.Div(id="movies-content")
    ]
)

@callback(
    Output("movies-content", "children"),
    Input("fetch-movies-btn", "n_clicks"),
    prevent_initial_call=True
)
def fetch_movies(n_clicks):
    """Henter film fra Trakt.tv API"""
    try:
        # Trakt.tv API - kræver client_id og client_secret
        client_id = os.getenv("TRAKT_CLIENT_ID", "your-client-id-here")
        
        headers = {
            "Content-Type": "application/json",
            "trakt-api-version": "2",
            "trakt-api-key": client_id
        }
        
        # Hent populære film
        url = "https://api.trakt.tv/movies/popular"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            movies = response.json()[:10]  # Første 10 film
            
            cards = []
            for movie in movies:
                title = movie.get("title", "No title")
                year = movie.get("year", "")
                overview = movie.get("overview", "No overview available")
                ids = movie.get("ids", {})
                trakt_id = ids.get("trakt", "")
                imdb_id = ids.get("imdb", "")
                
                card = dbc.Card(
                    [
                        dbc.CardBody(
                            [
                                html.H5(f"{title} ({year})", className="card-title"),
                                html.P(overview[:200] + "..." if len(overview) > 200 else overview, className="card-text"),
                                html.Small(f"Trakt ID: {trakt_id}", className="text-muted"),
                                html.Br(),
                                html.A(
                                    "Se på Trakt.tv",
                                    href=f"https://trakt.tv/movies/{trakt_id}",
                                    target="_blank",
                                    className="btn btn-sm btn-primary mt-2"
                                )
                            ]
                        )
                    ],
                    className="mb-3"
                )
                cards.append(card)
            
            return cards
        else:
            return dbc.Alert(f"Fejl ved hentning af film: {response.status_code}", color="danger")
    except Exception as e:
        return dbc.Alert(f"Fejl: {str(e)}", color="danger")

