import dash
from dash import html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import requests
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

dash.register_page(__name__, path="/books", name="Books")

layout = html.Div(
    [
        html.H2("Books - Sanity Database", className="mb-4"),
        html.P("Bøger fra din Sanity database."),
        dcc.Store(id="books-trigger", data=True),  # Trigger for automatisk hentning
        html.Div(id="books-content")
    ]
)

@callback(
    Output("books-content", "children"),
    Input("books-trigger", "data")
)
def fetch_books(trigger):
    """Henter bøger fra Sanity API automatisk"""
    try:
        # Sanity API konfiguration
        project_id = os.getenv("SANITY_PROJECT_ID", "")
        dataset = os.getenv("SANITY_DATASET", "production")
        api_version = os.getenv("SANITY_API_VERSION", "2023-01-01")
        
        if not project_id:
            return dbc.Alert(
                [
                    html.Strong("Sanity Project ID mangler!"),
                    html.Br(),
                    "Sæt venligst SANITY_PROJECT_ID i din .env fil."
                ],
                color="warning"
            )
        
        # Sanity GROQ query - hent alle felter
        query = '''*[_type == 'book'] {
            _id,
            _createdAt,
            _updatedAt,
            title,
            number,
            date,
            completed
        } | order(_createdAt desc) [0...20]'''
        
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
                number = book.get("number", "")
                date = book.get("date", "")
                completed = book.get("completed", False)
                created_at = book.get("_createdAt", "")
                updated_at = book.get("_updatedAt", "")
                
                # Formatér datoer
                formatted_date = ""
                if date:
                    try:
                        dt = datetime.strptime(date, "%Y-%m-%d")
                        formatted_date = dt.strftime("%d/%m/%Y")
                    except:
                        formatted_date = date
                
                formatted_created = ""
                if created_at:
                    try:
                        dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        formatted_created = dt.strftime("%d/%m/%Y")
                    except:
                        formatted_created = created_at[:10] if len(created_at) >= 10 else created_at
                
                # Opret card
                card = dbc.Card(
                    [
                        dbc.CardBody(
                            [
                                html.H4(title, className="card-title mb-2"),
                                html.Div(
                                    [
                                        html.Small(
                                            [
                                                f"Nummer: {number} | " if number else "",
                                                f"Dato: {formatted_date} | " if formatted_date else "",
                                                "✅ Færdig" if completed else "📖 I gang",
                                                f" | Oprettet: {formatted_created}" if formatted_created else ""
                                            ],
                                            className="text-muted d-block mb-2"
                                        )
                                    ]
                                )
                            ]
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
                html.H4("Mine Bøger", className="mb-3"),
                *cards
            ])
        elif response.status_code == 401:
            return dbc.Alert(
                [
                    html.Strong("401 Unauthorized"),
                    html.Br(),
                    "Tjek venligst at din Sanity Project ID er korrekt."
                ],
                color="danger"
            )
        else:
            error_msg = response.text if hasattr(response, 'text') else "Ukendt fejl"
            return dbc.Alert(
                [
                    html.Strong(f"Fejl ved hentning af bøger: {response.status_code}"),
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

