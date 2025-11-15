import dash
from dash import html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import requests
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

dash.register_page(__name__, path="/music", name="Music")

# Din YouTube playlist ID
PLAYLIST_ID = "PLkZ_a_mCRqgLgl3Gk4gd5cheR4IXmFwdB"

layout = html.Div(
    [
        html.H2("Music - YouTube Playlist", className="mb-4"),
        html.P("Min musik playlist fra YouTube."),
        dcc.Store(id="music-trigger", data=True),  # Trigger for automatisk hentning
        html.Div(id="music-content")
    ]
)

@callback(
    Output("music-content", "children"),
    Input("music-trigger", "data")
)
def fetch_music(trigger):
    """Henter videoer fra YouTube playlist automatisk"""
    try:
        # YouTube Data API v3
        api_key = os.getenv("YOUTUBE_API_KEY", "")
        
        if not api_key:
            return dbc.Alert(
                [
                    html.Strong("YouTube API nøgle mangler!"),
                    html.Br(),
                    "Sæt venligst YOUTUBE_API_KEY i din .env fil."
                ],
                color="warning"
            )
        
        # Hent playlist items
        url = "https://www.googleapis.com/youtube/v3/playlistItems"
        params = {
            "part": "snippet,contentDetails",
            "playlistId": PLAYLIST_ID,
            "maxResults": 50,
            "key": api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            items = data.get("items", [])
            
            if not items:
                return dbc.Alert("Ingen videoer fundet i playlisten", color="info")
            
            cards = []
            for item in items:
                snippet = item.get("snippet", {})
                video_id = snippet.get("resourceId", {}).get("videoId", "")
                title = snippet.get("title", "No title")
                description = snippet.get("description", "")
                channel_title = snippet.get("channelTitle", "")
                published_at = snippet.get("publishedAt", "")
                
                # Hent thumbnail - brug high quality hvis tilgængelig
                thumbnails = snippet.get("thumbnails", {})
                thumbnail = thumbnails.get("high", {}).get("url") or thumbnails.get("medium", {}).get("url") or thumbnails.get("default", {}).get("url", "")
                
                # Formatér dato
                formatted_date = ""
                if published_at:
                    try:
                        dt = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                        formatted_date = dt.strftime("%d/%m/%Y")
                    except:
                        formatted_date = published_at[:10] if len(published_at) >= 10 else published_at
                
                # Opret card med thumbnail og info
                card = dbc.Card(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    html.Img(
                                        src=thumbnail,
                                        style={
                                            "width": "100%",
                                            "height": "auto",
                                            "objectFit": "cover",
                                            "borderRadius": "8px"
                                        },
                                        className="img-fluid"
                                    ),
                                    width=4
                                ),
                                dbc.Col(
                                    dbc.CardBody(
                                        [
                                            html.H5(title, className="card-title mb-2"),
                                            html.P(
                                                description[:200] + "..." if len(description) > 200 else description,
                                                className="card-text",
                                                style={"fontSize": "0.9rem"}
                                            ),
                                            html.Div(
                                                [
                                                    html.Small(
                                                        [
                                                            f"Kanal: {channel_title} | " if channel_title else "",
                                                            f"Udgivet: {formatted_date}" if formatted_date else ""
                                                        ],
                                                        className="text-muted d-block mb-2"
                                                    ),
                                                    html.A(
                                                        "▶️ Se på YouTube",
                                                        href=f"https://www.youtube.com/watch?v={video_id}",
                                                        target="_blank",
                                                        className="btn btn-danger btn-sm"
                                                    )
                                                ]
                                            )
                                        ]
                                    ),
                                    width=8
                                )
                            ],
                            className="g-0"
                        )
                    ],
                    className="mb-4 shadow-sm",
                    style={
                        "borderRadius": "8px",
                        "border": "1px solid #e0e0e0"
                    }
                )
                cards.append(card)
            
            return html.Div([
                html.H4("Min Musik Playlist", className="mb-3"),
                *cards
            ])
        elif response.status_code == 401:
            return dbc.Alert(
                [
                    html.Strong("401 Unauthorized - API nøgle er ugyldig"),
                    html.Br(),
                    "Tjek venligst at din YOUTUBE_API_KEY i .env filen er korrekt."
                ],
                color="danger"
            )
        else:
            error_msg = response.text if hasattr(response, 'text') else "Ukendt fejl"
            return dbc.Alert(
                [
                    html.Strong(f"Fejl ved hentning af playlist: {response.status_code}"),
                    html.Br(),
                    error_msg[:200] if len(error_msg) > 200 else error_msg
                ],
                color="danger"
            )
    except Exception as e:
        return dbc.Alert(
            [
                html.Strong("Fejl:"),
                html.Br(),
                str(e)
            ],
            color="danger"
        )

