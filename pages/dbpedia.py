import dash
from dash import html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import requests
from SPARQLWrapper import SPARQLWrapper, JSON

dash.register_page(__name__, path="/dbpedia", name="DBpedia")

layout = html.Div(
    [
        html.H2("DBpedia - SPARQL Queries", className="mb-4"),
        html.P("Søg efter information fra DBpedia ved hjælp af SPARQL queries."),
        dbc.InputGroup(
            [
                dbc.Input(
                    id="dbpedia-search",
                    placeholder="Søg efter film, bøger, musik, osv... (f.eks. 'Harry Potter', 'The Beatles')",
                    type="text"
                ),
                dbc.Button("Søg", id="dbpedia-search-btn", color="primary")
            ],
            className="mb-4"
        ),
        dcc.Store(id="dbpedia-trigger", data=True),
        html.Div(id="dbpedia-content")
    ]
)

def execute_sparql_query(query):
    """Udfører en SPARQL query mod DBpedia"""
    try:
        # Brug DBpedia's offentlige SPARQL endpoint
        sparql = SPARQLWrapper("https://dbpedia.org/sparql")
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        sparql.setTimeout(60)  # Øg timeout til 60 sekunder
        sparql.setMethod("GET")  # Brug GET i stedet for POST for bedre caching
        results = sparql.query().convert()
        return results
    except Exception as e:
        return {"error": str(e)}

@callback(
    Output("dbpedia-content", "children"),
    Input("dbpedia-search-btn", "n_clicks"),
    Input("dbpedia-search", "n_submit"),
    Input("dbpedia-trigger", "data"),
    dash.dependencies.State("dbpedia-search", "value"),
    prevent_initial_call=False
)
def search_dbpedia(search_clicks, search_submit, trigger, search_term):
    """Søger i DBpedia baseret på søgeterm"""
    
    # Hvis der ikke er en søgeterm, vis eksempel queries
    if not search_term:
        return html.Div([
            dbc.Alert(
                [
                    html.Strong("Velkommen til DBpedia søgning!"),
                    html.Br(),
                    "Indtast en søgeterm for at finde information fra DBpedia. ",
                    "Du kan søge efter film, bøger, musikere, osv."
                ],
                color="info",
                className="mb-4"
            ),
            html.H4("Eksempel queries:", className="mb-3"),
            dbc.Card(
                [
                    dbc.CardBody(
                        [
                            html.H5("Populære film", className="card-title"),
                            html.P("Henter information om populære film fra DBpedia."),
                            dbc.Button(
                                "Kør eksempel query",
                                id="example-movies-btn",
                                color="secondary",
                                size="sm",
                                className="mt-2"
                            )
                        ]
                    )
                ],
                className="mb-3"
            )
        ])
    
    # Byg SPARQL query - meget simplificeret for bedre performance
    search_term_clean = search_term.strip()
    
    # Brug en meget simplere query - søg kun på Film først (hurtigere)
    # Hvis det virker, kan vi udvide til andre typer
    query = f"""
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX dbo: <http://dbpedia.org/ontology/>
    
    SELECT DISTINCT ?subject ?label ?abstract
    WHERE {{
        ?subject rdf:type dbo:Film .
        ?subject rdfs:label ?label .
        FILTER (lang(?label) = "en")
        FILTER (contains(lcase(?label), lcase("{search_term_clean}")))
        OPTIONAL {{ 
            ?subject rdfs:comment ?abstract .
            FILTER (lang(?abstract) = "en")
        }}
    }}
    LIMIT 10
    """
    
    results = execute_sparql_query(query)
    
    # Debug: Vis query hvis fejl
    if "error" in results:
        return dbc.Alert(
            [
                html.Strong("Fejl ved SPARQL query:"),
                html.Br(),
                str(results["error"]),
                html.Br(),
                html.Br(),
                html.Small(f"Query: {query[:200]}...")
            ],
            color="danger"
        )
    
    # Tjek om results har den rigtige struktur
    if not isinstance(results, dict):
        return dbc.Alert(
            [
                html.Strong("Uventet svar fra DBpedia:"),
                html.Br(),
                f"Type: {type(results)}",
                html.Br(),
                f"Data: {str(results)[:200]}"
            ],
            color="warning"
        )
    
    bindings = results.get("results", {}).get("bindings", [])
    
    if not bindings:
        return dbc.Alert(
            f"Ingen resultater fundet for '{search_term}'. Prøv en anden søgeterm.",
            color="info"
        )
    
    cards = []
    for binding in bindings:
        subject = binding.get("subject", {}).get("value", "") if binding.get("subject") else ""
        label = binding.get("label", {}).get("value", "") if binding.get("label") else "No label"
        abstract_obj = binding.get("abstract", {})
        abstract = abstract_obj.get("value", "No description available") if abstract_obj else "No description available"
        # Type er nu hardcoded til Film i queryen
        type_name = "Film"
        
        card = dbc.Card(
            [
                dbc.CardBody(
                    [
                        html.H5(label, className="card-title mb-2"),
                        html.Small(
                            f"Type: {type_name}",
                            className="text-muted d-block mb-2"
                        ),
                        html.P(
                            abstract[:300] + "..." if len(abstract) > 300 else abstract,
                            className="card-text"
                        ),
                        html.A(
                            "Se på DBpedia",
                            href=subject,
                            target="_blank",
                            className="btn btn-sm btn-primary mt-2"
                        )
                    ]
                )
            ],
            className="mb-3 shadow-sm"
        )
        cards.append(card)
    
    return html.Div([
        html.H4(f"Resultater for: '{search_term}'", className="mb-3"),
        *cards
    ])

