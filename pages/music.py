import dash
from dash import html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import requests
import os
from dotenv import load_dotenv

load_dotenv()

dash.register_page(__name__, path="/music", name="Music")

layout = html.Div(
        [
            html.H2("Music - YouTube Playlist", className="mb-4"),
            html.P("Henter musik fra din YouTube playlist."),
            dbc.Input(
                id="playlist-id-input",
                placeholder="Indtast YouTube Playlist ID",
                className="mb-3",
                style={"maxWidth": "500px"}
            ),
            dbc.Button("Hent Playlist", id="fetch-music-btn", color="primary", className="mb-3"),
            html.Div(id="music-content")
        ]
)

@callback(
    Output("music-content", "children"),
    Input("fetch-music-btn", "n_clicks"),
    Input("playlist-id-input", "value"),
    prevent_initial_call=True
)
def fetch_music(n_clicks, playlist_id):
    """Henter videoer fra YouTube playlist"""
    if not playlist_id:
        return dbc.Alert("Indtast venligst et Playlist ID", color="warning")
    
    try:
        # YouTube Data API v3
        api_key = os.getenv("YOUTUBE_API_KEY", "your-api-key-here")
        
        # Først hent playlist items
        url = f"https://www.googleapis.com/youtube/v3/playlistItems"
        params = {
            "part": "snippet",
            "playlistId": playlist_id,
            "maxResults": 10,
            "key": api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            items = data.get("items", [])
            
            cards = []
            for item in items:
                snippet = item.get("snippet", {})
                video_id = snippet.get("resourceId", {}).get("videoId", "")
                title = snippet.get("title", "No title")
                thumbnail = snippet.get("thumbnails", {}).get("default", {}).get("url", "")
                
                card = dbc.Card(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    html.Img(src=thumbnail, style={"width": "100%"}),
                                    width=3
                                ),
                                dbc.Col(
                                    dbc.CardBody(
                                        [
                                            html.H5(title, className="card-title"),
                                            html.A(
                                                "Se på YouTube",
                                                href=f"https://www.youtube.com/watch?v={video_id}",
                                                target="_blank",
                                                className="btn btn-sm btn-danger mt-2"
                                            )
                                        ]
                                    ),
                                    width=9
                                )
                            ],
                            className="g-0"
                        )
                    ],
                    className="mb-3"
                )
                cards.append(card)
            
            return cards if cards else dbc.Alert("Ingen videoer fundet", color="info")
        else:
            return dbc.Alert(f"Fejl ved hentning af playlist: {response.status_code}", color="danger")
    except Exception as e:
        return dbc.Alert(f"Fejl: {str(e)}", color="danger")

