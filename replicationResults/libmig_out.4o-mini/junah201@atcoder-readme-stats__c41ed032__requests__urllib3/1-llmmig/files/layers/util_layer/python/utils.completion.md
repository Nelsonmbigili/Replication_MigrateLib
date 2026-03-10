### Explanation of Changes
To migrate the code from using the `requests` library to the `urllib3` library, the following changes were made:

1. **Importing `urllib3`**: The `requests` library was replaced with `urllib3`. The `requests` module is not needed anymore.
2. **Creating a PoolManager**: `urllib3` requires a `PoolManager` instance to handle connections. This was created to manage the HTTP requests.
3. **Making the GET Request**: The `requests.get()` method was replaced with `http.request('GET', url)`, where `http` is the `PoolManager` instance.
4. **Accessing Response Data**: The response from `urllib3` is accessed via `response.data`, which is in bytes, so it needs to be decoded to a string using `.decode('utf-8')`.
5. **Error Handling**: The error handling for user not found and unrated users remains the same, as it relies on parsing the HTML response.

Here is the modified code:

```python
from dataclasses import dataclass
from typing import Optional
from enum import Enum, unique

import urllib3
from bs4 import BeautifulSoup

http = urllib3.PoolManager()

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
    response = http.request('GET', url)

    soup = BeautifulSoup(response.data.decode('utf-8'), "html.parser")

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