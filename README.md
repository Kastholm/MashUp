# MashUp Dashboard

Et Dash dashboard projekt med integration til flere API'er.

## Features

- **News**: Henter nyheder fra New York Times API
- **Music**: Henter musik fra YouTube playlists
- **Movies**: Henter film fra Trakt.tv API
- **Books**: Henter bøger fra Sanity database
- **Chuck Norris Joke**: Altid synligt banner med tilfældige Chuck Norris jokes

## Installation

1. Opret et virtuelt miljø:
```bash
python -m venv venv
```

2. Aktiver det virtuelle miljø:
```bash
# Linux/Mac:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

3. Installer dependencies:
```bash
pip install -r requirements.txt
```

eller

```bash
pip install -e .
```

4. Opret `.env` fil med dine API nøgler:
```bash
cp .env.example .env
```

Rediger `.env` filen og tilføj dine API nøgler:
- `NYT_API_KEY`: New York Times API key
- `YOUTUBE_API_KEY`: YouTube Data API key
- `TRAKT_CLIENT_ID`: Trakt.tv client ID
- `SANITY_PROJECT_ID`: Sanity project ID
- `SANITY_DATASET`: Sanity dataset navn (typisk "production")

## Kørsel

Kør applikationen med:
```bash
python app.py
```

Applikationen vil være tilgængelig på: http://127.0.0.1:8050

## Projektstruktur

```
MashUp/
├── app.py              # Hovedapplikation med navigation
├── pages/              # Side mapper
│   ├── __init__.py
│   ├── home.py        # Home page
│   ├── news.py        # News page (New York Times)
│   ├── music.py       # Music page (YouTube)
│   ├── movies.py      # Movies page (Trakt.tv)
│   └── books.py       # Books page (Sanity)
├── utils/             # Utility funktioner
│   ├── __init__.py
│   └── chuck_norris.py # Chuck Norris joke funktioner
├── pyproject.toml     # Projekt konfiguration
├── requirements.txt   # Python dependencies
├── .env.example       # Eksempel på environment variabler
└── README.md         # Denne fil
```

## API'er

Projektet bruger følgende API'er:
- **Chuck Norris API**: https://api.chucknorris.io/ (ingen API key nødvendig)
- **New York Times API**: https://developer.nytimes.com/
- **YouTube Data API**: https://developers.google.com/youtube/v3
- **Trakt.tv API**: https://trakt.docs.apiary.io/
- **Sanity API**: https://www.sanity.io/docs

