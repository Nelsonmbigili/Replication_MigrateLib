### Explanation of Changes
To migrate the code from using the `requests` library to the `treq` library, the following changes were made:
1. **Import Changes**: Removed the `requests` import and replaced it with `treq`.
2. **Asynchronous Nature of `treq`**: Since `treq` is an asynchronous library, the `get_user_data` function was modified to be asynchronous (`async def`) and the `requests.get` call was replaced with `treq.get`.
3. **Handling Responses**: `treq` returns a `Response` object, which requires asynchronous methods to read the response content. The `response.text` was replaced with `await response.text()` to retrieve the response body.
4. **Calling the Function**: Since the function is now asynchronous, it must be awaited when called. This change is not reflected in the provided code because the calling context is not included.

### Modified Code
```python
from dataclasses import dataclass
from typing import Optional
from enum import Enum, unique

import treq
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


async def get_user_data(username: str) -> Optional[UserData]:
    """Get user data from atcoder"""
    url = f"https://atcoder.jp/users/{username}"
    response = await treq.get(url)
    response_text = await response.text()

    soup = BeautifulSoup(response_text, "html.parser")

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

### Notes
1. The `get_user_data` function is now asynchronous and must be awaited when called. Ensure that the calling code is updated to handle this change (e.g., using `await get_user_data(username)` or running it in an event loop).
2. The rest of the code remains unchanged, as the migration only affects the HTTP request and response handling.