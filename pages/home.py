import dash
from dash import html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import requests
import os
from dotenv import load_dotenv
import plotly.graph_objs as go

load_dotenv()

dash.register_page(__name__, path="/")

layout = html.Div(
    [
        html.H2("Dashboard Oversigt", className="mb-4"),
        html.P("Velkommen til MashUp Dashboard! Her er en oversigt over data fra dine API'er."),
        
        # Info boxes med statistikker
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardBody(
                                [
                                    html.H4(id="movies-count", children="0", className="text-primary"),
                                    html.P("Film set", className="mb-0")
                                ]
                            )
                        ],
                        className="text-center shadow-sm"
                    ),
                    width=3
                ),
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardBody(
                                [
                                    html.H4(id="books-count", children="0", className="text-success"),
                                    html.P("Bøger", className="mb-0")
                                ]
                            )
                        ],
                        className="text-center shadow-sm"
                    ),
                    width=3
                ),
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardBody(
                                [
                                    html.H4(id="news-count", children="0", className="text-info"),
                                    html.P("Nyheder (7 dage)", className="mb-0")
                                ]
                            )
                        ],
                        className="text-center shadow-sm"
                    ),
                    width=3
                ),
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardBody(
                                [
                                    html.H4(id="music-count", children="0", className="text-danger"),
                                    html.P("Musik videoer", className="mb-0")
                                ]
                            )
                        ],
                        className="text-center shadow-sm"
                    ),
                    width=3
                )
            ],
            className="mb-4"
        ),
        
        # Dash grafer
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader("Film over tid"),
                                dbc.CardBody(
                                    dcc.Graph(id="movies-timeline")
                                )
                            ],
                            className="shadow-sm mb-4"
                        )
                    ],
                    width=6
                ),
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader("Bøger Status"),
                                dbc.CardBody(
                                    dcc.Graph(id="books-status")
                                )
                            ],
                            className="shadow-sm mb-4"
                        )
                    ],
                    width=6
                )
            ]
        ),
        
        dcc.Store(id="home-data-trigger", data=True)
    ]
)

@callback(
    [Output("movies-count", "children"),
     Output("books-count", "children"),
     Output("news-count", "children"),
     Output("music-count", "children"),
     Output("movies-timeline", "figure"),
     Output("books-status", "figure")],
    Input("home-data-trigger", "data")
)
def update_dashboard(trigger):
    """Henter data fra alle API'er og opdaterer dashboard"""
    
    # Hent film count
    movies_count = 0
    movies_timeline_data = []
    try:
        trakt_username = os.getenv("TRAKT_USERNAME", "")
        trakt_client_id = os.getenv("TRAKT_CLIENT_ID", "")
        if trakt_username and trakt_client_id:
            headers = {
                "Content-Type": "application/json",
                "trakt-api-version": "2",
                "trakt-api-key": trakt_client_id
            }
            url = f"https://api.trakt.tv/users/{trakt_username}/history/movies"
            response = requests.get(url, headers=headers, params={"limit": 100}, timeout=5)
            if response.status_code == 200:
                movies = response.json()
                movies_count = len(movies)
                # Opret timeline data
                from datetime import datetime
                dates = []
                for movie in movies[:20]:  # Første 20
                    watched_at = movie.get("watched_at", "")
                    if watched_at:
                        try:
                            dt = datetime.fromisoformat(watched_at.replace('Z', '+00:00'))
                            dates.append(dt.strftime("%Y-%m"))
                        except:
                            pass
                if dates:
                    from collections import Counter
                    date_counts = Counter(dates)
                    movies_timeline_data = [
                        go.Bar(
                            x=list(date_counts.keys()),
                            y=list(date_counts.values()),
                            marker_color='#007bff'
                        )
                    ]
    except:
        pass
    
    # Hent bøger count
    books_count = 0
    books_completed = 0
    books_in_progress = 0
    try:
        project_id = os.getenv("SANITY_PROJECT_ID", "")
        dataset = os.getenv("SANITY_DATASET", "production")
        api_version = os.getenv("SANITY_API_VERSION", "2023-01-01")
        if project_id:
            query = "*[_type == 'book']"
            url = f"https://{project_id}.api.sanity.io/v{api_version}/data/query/{dataset}"
            response = requests.get(url, params={"query": query}, timeout=5)
            if response.status_code == 200:
                books = response.json().get("result", [])
                books_count = len(books)
                books_completed = sum(1 for b in books if b.get("completed", False))
                books_in_progress = books_count - books_completed
    except:
        pass
    
    # Hent nyheder count
    news_count = 0
    try:
        api_key = os.getenv("NYT_API_KEY", "")
        if api_key:
            url = "https://api.nytimes.com/svc/mostpopular/v2/viewed/7.json"
            response = requests.get(url, params={"api-key": api_key}, timeout=5)
            if response.status_code == 200:
                news_count = len(response.json().get("results", []))
    except:
        pass
    
    # Hent musik count (placeholder - kan ikke hente uden playlist access)
    music_count = 0
    
    # Opret grafer
    movies_fig = {
        "data": movies_timeline_data if movies_timeline_data else [go.Bar(x=[], y=[])],
        "layout": go.Layout(
            title="Film set per måned",
            xaxis={"title": "Måned"},
            yaxis={"title": "Antal film"},
            margin={"l": 40, "r": 10, "t": 40, "b": 40}
        )
    }
    
    books_fig = {
        "data": [
            go.Pie(
                labels=["Færdige", "I gang"],
                values=[books_completed, books_in_progress],
                hole=0.4,
                marker_colors=['#28a745', '#ffc107']
            )
        ],
        "layout": go.Layout(
            title="Bøger Status",
            margin={"l": 40, "r": 40, "t": 40, "b": 40}
        )
    }
    
    return (
        movies_count,
        books_count,
        news_count,
        music_count,
        movies_fig,
        books_fig
    )

