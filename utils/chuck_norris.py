import requests
from dash import html
import dash_bootstrap_components as dbc

def get_chuck_norris_joke():
    """Henter en Chuck Norris joke fra API"""
    try:
        response = requests.get("https://api.chucknorris.io/jokes/random", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get("value", "Chuck Norris doesn't need jokes, jokes need Chuck Norris.")
        return "Chuck Norris is loading..."
    except Exception as e:
        return f"Chuck Norris error: {str(e)}"

def create_chuck_norris_banner():
    """Opretter en banner komponent med Chuck Norris joke"""
    joke = get_chuck_norris_joke()
    return dbc.Alert(
        [
            html.Strong("Chuck Norris Joke: "),
            joke
        ],
        color="warning",
        className="mb-3",
        style={"fontSize": "0.9rem"}
    )

