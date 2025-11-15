import dash
from dash import html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import requests
import os
from dotenv import load_dotenv

load_dotenv()

dash.register_page(__name__, path="/books", name="Books")

layout = html.Div(
    [
        html.H2("Books - Sanity Database", className="mb-4"),
        html.P("Henter bøger fra din Sanity database."),
        dbc.Button("Hent Bøger", id="fetch-books-btn", color="primary", className="mb-3"),
        html.Div(id="books-content")
    ]
)

@callback(
    Output("books-content", "children"),
    Input("fetch-books-btn", "n_clicks"),
    prevent_initial_call=True
)
def fetch_books(n_clicks):
    """Henter bøger fra Sanity API"""
    try:
        # Sanity API konfiguration
        project_id = os.getenv("SANITY_PROJECT_ID", "your-project-id")
        dataset = os.getenv("SANITY_DATASET", "production")
        api_version = os.getenv("SANITY_API_VERSION", "2023-01-01")
        
        # Sanity GROQ query
        query = "*[_type == 'book'] | order(_createdAt desc) [0...10]"
        
        url = f"https://{project_id}.api.sanity.io/v{api_version}/data/query/{dataset}"
        params = {
            "query": query
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            books = data.get("result", [])
            
            if not books:
                return dbc.Alert("Ingen bøger fundet i databasen", color="info")
            
            cards = []
            for book in books:
                title = book.get("title", "No title")
                author = book.get("author", "Unknown author")
                description = book.get("description", "No description available")
                
                card = dbc.Card(
                    [
                        dbc.CardBody(
                            [
                                html.H5(title, className="card-title"),
                                html.P(html.Strong(f"Af: {author}"), className="card-text"),
                                html.P(description[:200] + "..." if len(description) > 200 else description),
                            ]
                        )
                    ],
                    className="mb-3"
                )
                cards.append(card)
            
            return cards
        else:
            return dbc.Alert(f"Fejl ved hentning af bøger: {response.status_code}", color="danger")
    except Exception as e:
        return dbc.Alert(f"Fejl: {str(e)}", color="danger")

