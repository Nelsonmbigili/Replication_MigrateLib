import requests


def page_exists(url: str) -> bool:
    response = requests.head(url)
    return response.status_code == 200


def read_page(url: str) -> str:
    response = requests.get(url)
    response.raise_for_status()
    return response.text
