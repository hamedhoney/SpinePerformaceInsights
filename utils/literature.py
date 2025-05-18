import requests

def search_crossref(query, rows=5):
    url = "https://api.crossref.org/works"
    params = {
        "query": query,
        "rows": rows,
        "filter": "type:journal-article",
        "select": "title,author,abstract,DOI,published-print,container-title",
        "sort": "relevance"
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()["message"]["items"]
