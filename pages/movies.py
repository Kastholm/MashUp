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
        html.P("Din film historik fra Trakt.tv."),
        dcc.Store(id="movies-trigger", data=True),  # Trigger for automatisk hentning
        html.Div(id="movies-content")
    ]
)

@callback(
    Output("movies-content", "children"),
    Input("movies-trigger", "data")
)
def fetch_movies(trigger):
    """Henter brugerens film historik fra Trakt.tv API automatisk"""
    # Brug brugernavn fra environment variable
    trakt_username = os.getenv("TRAKT_USERNAME", "")
    
    if not trakt_username:
        return dbc.Alert("Indtast venligst dit Trakt.tv brugernavn eller sæt TRAKT_USERNAME i .env filen", color="warning")
    
    try:
        # Trakt.tv API - kræver client_id
        client_id = os.getenv("TRAKT_CLIENT_ID", "your-client-id-here")
        
        headers = {
            "Content-Type": "application/json",
            "trakt-api-version": "2",
            "trakt-api-key": client_id
        }
        
        # Hent brugerens film historik
        url = f"https://api.trakt.tv/users/{trakt_username}/history/movies"
        params = {
            "limit": 20  # Hent de seneste 20 film
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            history_items = response.json()
            
            if not history_items:
                return dbc.Alert("Ingen film historik fundet. Har du set nogen film på Trakt.tv?", color="info")
            
            cards = []
            for item in history_items:
                movie = item.get("movie", {})
                watched_at = item.get("watched_at", "")
                
                title = movie.get("title", "No title")
                year = movie.get("year", "")
                overview = movie.get("overview", "No overview available")
                ids = movie.get("ids", {})
                trakt_id = ids.get("trakt", "")
                slug = ids.get("slug", "")
                
                # Formatér dato
                if watched_at:
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(watched_at.replace('Z', '+00:00'))
                        watched_date = dt.strftime("%d/%m/%Y %H:%M")
                    except:
                        watched_date = watched_at
                else:
                    watched_date = "Ukendt dato"
                
                card = dbc.Card(
                    [
                        dbc.CardBody(
                            [
                                html.H5(f"{title} ({year})", className="card-title"),
                                html.P(overview[:200] + "..." if len(overview) > 200 else overview, className="card-text"),
                                html.Small(f"Set: {watched_date}", className="text-muted"),
                                html.Br(),
                                html.A(
                                    "Se på Trakt.tv",
                                    href=f"https://trakt.tv/movies/{slug}" if slug else f"https://trakt.tv/movies/{trakt_id}",
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
        elif response.status_code == 404:
            return dbc.Alert(f"Bruger '{trakt_username}' ikke fundet. Tjek dit brugernavn.", color="warning")
        else:
            return dbc.Alert(f"Fejl ved hentning af film historik: {response.status_code} - {response.text}", color="danger")
    except Exception as e:
        return dbc.Alert(f"Fejl: {str(e)}", color="danger")

