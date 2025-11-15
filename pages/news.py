import dash
from dash import html, dcc, callback, Output, Input, State
import dash_bootstrap_components as dbc
import requests
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

dash.register_page(__name__, path="/news", name="News")

layout = html.Div(
    [
        html.H2("News - New York Times", className="mb-4"),
        html.P("De mest sete artikler på 7 dage og søg efter artikler."),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.InputGroup(
                            [
                                dbc.Input(
                                    id="search-query",
                                    placeholder="Søg efter artikler...",
                                    type="text",
                                    n_submit=0
                                ),
                                dbc.Button("Søg", id="search-btn", color="primary")
                            ],
                            className="mb-3"
                        )
                    ],
                    width=8
                ),
                dbc.Col(
                    dbc.Button("Vis Mest Sete", id="show-most-viewed-btn", color="secondary", outline=True),
                    width=4
                )
            ],
            className="mb-4"
        ),
        dcc.Store(id="news-trigger", data="most-viewed"),  # Trigger for automatisk hentning
        html.Div(id="news-content")
    ]
)

def create_article_card(article):
    """Opretter en card komponent for en artikel"""
    title = article.get("title", "No title")
    abstract = article.get("abstract", "No abstract")
    byline = article.get("byline", "")
    url = article.get("url", "#")
    published_date = article.get("published_date", "")
    section = article.get("section", "")
    
    # Hent billede hvis tilgængeligt
    media = article.get("media", [])
    image_url = None
    if media and isinstance(media, list) and len(media) > 0:
        # Tjek om første element er et dictionary
        first_media = media[0]
        if isinstance(first_media, dict):
            media_metadata = first_media.get("media-metadata", [])
            if media_metadata and isinstance(media_metadata, list) and len(media_metadata) > 0:
                # Find største billede (typisk det sidste)
                for img in media_metadata:
                    if isinstance(img, dict):
                        if img.get("format") == "superJumbo" or img.get("format") == "large":
                            image_url = img.get("url")
                            break
                # Hvis ikke fundet, tag det sidste
                if not image_url and len(media_metadata) > 0:
                    last_img = media_metadata[-1]
                    if isinstance(last_img, dict):
                        image_url = last_img.get("url")
    
    # Formatér dato
    if published_date:
        try:
            dt = datetime.strptime(published_date, "%Y-%m-%d")
            formatted_date = dt.strftime("%d/%m/%Y")
        except:
            formatted_date = published_date
    else:
        formatted_date = ""
    
    # Opret card med billede hvis tilgængeligt
    if image_url:
        card_content = dbc.Row(
            [
                dbc.Col(
                    html.Img(
                        src=image_url,
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
                            html.P(abstract, className="card-text", style={"fontSize": "0.95rem"}),
                            html.Div(
                                [
                                    html.Small(
                                        [
                                            html.Strong("Af: ") if byline else "",
                                            byline if byline else "",
                                            " | " if byline and section else "",
                                            section if section else "",
                                            " | " if formatted_date else "",
                                            formatted_date if formatted_date else ""
                                        ],
                                        className="text-muted d-block mb-2"
                                    ),
                                    html.A(
                                        "Læs mere →",
                                        href=url,
                                        target="_blank",
                                        className="btn btn-primary btn-sm"
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
    else:
        card_content = dbc.CardBody(
            [
                html.H5(title, className="card-title mb-2"),
                html.P(abstract, className="card-text", style={"fontSize": "0.95rem"}),
                html.Div(
                    [
                        html.Small(
                            [
                                html.Strong("Af: ") if byline else "",
                                byline if byline else "",
                                " | " if byline and section else "",
                                section if section else "",
                                " | " if formatted_date else "",
                                formatted_date if formatted_date else ""
                            ],
                            className="text-muted d-block mb-2"
                        ),
                        html.A(
                            "Læs mere →",
                            href=url,
                            target="_blank",
                            className="btn btn-primary btn-sm"
                        )
                    ]
                )
            ]
        )
    
    return dbc.Card(
        card_content,
        className="mb-4 shadow-sm",
        style={
            "borderRadius": "8px",
            "border": "1px solid #e0e0e0"
        }
    )

@callback(
    Output("news-content", "children"),
    Input("news-trigger", "data"),
    Input("search-btn", "n_clicks"),
    Input("search-query", "n_submit"),
    Input("show-most-viewed-btn", "n_clicks"),
    State("search-query", "value"),
    prevent_initial_call=False
)
def fetch_news(trigger, search_clicks, search_submit, most_viewed_clicks, search_query):
    """Henter nyheder fra New York Times API"""
    api_key = os.getenv("NYT_API_KEY", "")
    
    # Tjek om API nøgle er sat
    if not api_key or api_key == "your-api-key-here":
        return dbc.Alert(
            [
                html.Strong("API nøgle mangler!"),
                html.Br(),
                "Sæt venligst NYT_API_KEY i din .env fil. ",
                html.A("Hent API nøgle her", href="https://developer.nytimes.com/get-started", target="_blank")
            ],
            color="warning"
        )
    
    # Bestem hvilken type data der skal hentes
    ctx = dash.callback_context
    if not ctx.triggered:
        # Første load - vis mest sete
        mode = "most-viewed"
    else:
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if (trigger_id == "search-btn" or trigger_id == "search-query") and search_query:
            mode = "search"
        elif trigger_id == "show-most-viewed-btn":
            mode = "most-viewed"
        else:
            mode = trigger if isinstance(trigger, str) else "most-viewed"
    
    try:
        if mode == "search" and search_query:
            # Søg efter artikler
            url = "https://api.nytimes.com/svc/search/v2/articlesearch.json"
            params = {
                "api-key": api_key,
                "q": search_query,
                "sort": "newest",
                "page": 0
            }
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get("response", {}).get("docs", [])[:20]
                
                if not articles:
                    return dbc.Alert(f"Ingen artikler fundet for '{search_query}'", color="info")
                
                cards = []
                for article in articles:
                    # Konverter search resultat format til samme format som most viewed
                    multimedia = article.get("multimedia", [])
                    # Find billede fra multimedia array
                    media_list = []
                    if multimedia and isinstance(multimedia, list):
                        # Search API har et andet format - find billede med type "image"
                        for media_item in multimedia:
                            if isinstance(media_item, dict) and media_item.get("type") == "image":
                                # Opret media-metadata format som most viewed API
                                media_url = media_item.get('url', '')
                                if media_url:
                                    # Hvis URL ikke starter med http, tilføj NYT base URL
                                    if not media_url.startswith('http'):
                                        media_url = f"https://www.nytimes.com/{media_url}"
                                    media_list.append({
                                        "media-metadata": [{
                                            "url": media_url,
                                            "format": media_item.get("subtype", "medium")
                                        }]
                                    })
                                    break
                    
                    # Håndter headline - kan være dict eller string
                    headline = article.get("headline", {})
                    if isinstance(headline, dict):
                        title = headline.get("main", "No title")
                    else:
                        title = str(headline) if headline else "No title"
                    
                    # Håndter byline - kan være dict eller string
                    byline_obj = article.get("byline", {})
                    if isinstance(byline_obj, dict):
                        byline = byline_obj.get("original", "")
                    else:
                        byline = str(byline_obj) if byline_obj else ""
                    
                    article_data = {
                        "title": title,
                        "abstract": article.get("abstract", "No abstract"),
                        "byline": byline,
                        "url": article.get("web_url", "#"),
                        "published_date": article.get("pub_date", "").split("T")[0] if article.get("pub_date") else "",
                        "section": article.get("section_name", ""),
                        "media": media_list
                    }
                    cards.append(create_article_card(article_data))
                
                return html.Div([
                    html.H4(f"Søgeresultater for: '{search_query}'", className="mb-3"),
                    *cards
                ])
            elif response.status_code == 401:
                return dbc.Alert(
                    [
                        html.Strong("401 Unauthorized - API nøgle er ugyldig eller mangler"),
                        html.Br(),
                        "Tjek venligst at din NYT_API_KEY i .env filen er korrekt."
                    ],
                    color="danger"
                )
            else:
                error_msg = response.text if hasattr(response, 'text') else "Ukendt fejl"
                return dbc.Alert(
                    [
                        html.Strong(f"Fejl ved søgning: {response.status_code}"),
                        html.Br(),
                        error_msg[:200] if len(error_msg) > 200 else error_msg
                    ],
                    color="danger"
                )
        
        else:
            # Hent mest sete artikler (7 dage)
            url = f"https://api.nytimes.com/svc/mostpopular/v2/viewed/7.json"
            params = {
                "api-key": api_key
            }
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get("results", [])[:20]
                
                if not articles:
                    return dbc.Alert("Ingen artikler fundet", color="info")
                
                cards = []
                for article in articles:
                    cards.append(create_article_card(article))
                
                return html.Div([
                    html.H4("Mest Sete Artikler (7 dage)", className="mb-3"),
                    *cards
                ])
            elif response.status_code == 401:
                return dbc.Alert(
                    [
                        html.Strong("401 Unauthorized - API nøgle er ugyldig eller mangler"),
                        html.Br(),
                        "Tjek venligst at din NYT_API_KEY i .env filen er korrekt. ",
                        html.A("Hent API nøgle her", href="https://developer.nytimes.com/get-started", target="_blank")
                    ],
                    color="danger"
                )
            else:
                error_msg = response.text if hasattr(response, 'text') else "Ukendt fejl"
                return dbc.Alert(
                    [
                        html.Strong(f"Fejl ved hentning af nyheder: {response.status_code}"),
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

