### Explanation of Changes
To migrate the code from using the `requests` library to `urllib3`, the following changes were made:
1. **Importing `urllib3`**: The `requests` library was removed, and `urllib3` was imported instead.
2. **HTTP Request**: The `requests.get` method was replaced with `urllib3.PoolManager` to make HTTP GET requests.
3. **Response Handling**: The `urllib3` response object requires explicit decoding of the response body using `.data.decode('utf-8')` to get the text content, as opposed to `requests` which provides `.text` directly.
4. **Error Handling**: The `urllib3` library does not raise exceptions for HTTP errors by default. However, since the original code does not handle HTTP errors explicitly, no additional error handling was added to maintain the original behavior.

### Modified Code
```python
from dataclasses import dataclass
from typing import Optional
from enum import Enum, unique

import urllib3
from bs4 import BeautifulSoup


@unique
class Tier(Enum):
    Unrated = "Unrated"
    _20_Kyu = "20 Kyu"
    _19_Kyu = "19 Kyu"
    _18_Kyu = "18 Kyu"
    _17_Kyu = "17 Kyu"
    _16_Kyu = "16 Kyu"
    _15_Kyu = "15 Kyu"
    _14_Kyu = "14 Kyu"
    _13_Kyu = "13 Kyu"
    _12_Kyu = "12 Kyu"
    _11_Kyu = "11 Kyu"
    _10_Kyu = "10 Kyu"
    _9_Kyu = "9 Kyu"
    _8_Kyu = "8 Kyu"
    _7_Kyu = "7 Kyu"
    _6_Kyu = "6 Kyu"
    _5_Kyu = "5 Kyu"
    _4_Kyu = "4 Kyu"
    _3_Kyu = "3 Kyu"
    _2_Kyu = "2 Kyu"
    _1_Kyu = "1 Kyu"
    _1_Dan = "1 Dan"
    _2_Dan = "2 Dan"
    _3_Dan = "3 Dan"
    _4_Dan = "4 Dan"
    _5_Dan = "5 Dan"
    _6_Dan = "6 Dan"
    _7_Dan = "7 Dan"
    _8_Dan = "8 Dan"
    _9_Dan = "9 Dan"
    _10_Dan = "10 Dan"
    Legend = "Legend"
    King = "King"


@dataclass
class UserData:
    username: str
    rank: str
    rating: int
    highest_rating: int
    tier: str
    matches: int

    def __str__(self):
        return f"UserData(username={self.username} rank={self.rank} rating={self.rating} highest_rating={self.highest_rating} tier={self.tier.value} matches={self.matches})"

    def __repr__(self):
        return f"UserData(username={self.username} rank={self.rank} rating={self.rating} highest_rating={self.highest_rating} tier={self.tier.value} matches={self.matches})"


def get_user_data(username: str) -> Optional[UserData]:
    """Get user data from atcoder"""
    url = f"https://atcoder.jp/users/{username}"
    http = urllib3.PoolManager()
    response = http.request("GET", url)

    soup = BeautifulSoup(response.data.decode("utf-8"), "html.parser")

    # user not found
    if soup.select_one("div.alert.alert-danger"):
        return None

    user_data = soup.select("table.dl-table.mt-2 > tr")

    # user is unrated
    if not user_data:
        return UserData(username, "Unrated", 0, 0, "Unrated", 0)

    rank = user_data[0].select_one("td").text
    rating = int(user_data[1].select_one(
        "td > span").text)
    highest_rating = int(user_data[2].select_one(
        "td > span").text)
    matches = int(user_data[3].select_one("td").text)
    tier = user_data[2].select_one(
        "td > span.bold").text

    return UserData(username, rank, rating, highest_rating, tier, matches)
```

### Summary of Changes
- Replaced `requests.get(url)` with `urllib3.PoolManager().request("GET", url)`.
- Used `response.data.decode("utf-8")` to decode the response body into a string for parsing with BeautifulSoup.
- Removed the `requests` import and added the `urllib3` import.