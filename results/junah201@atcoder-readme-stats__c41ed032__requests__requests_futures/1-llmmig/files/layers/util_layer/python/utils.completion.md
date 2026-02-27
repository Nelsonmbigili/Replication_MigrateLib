### Explanation of Changes
To migrate the code from using the `requests` library to `requests_futures`, the following changes were made:
1. **Import Change**: Replaced the `requests` import with `requests_futures.sessions` to use the `FuturesSession` class.
2. **Session Initialization**: Created an instance of `FuturesSession` to handle asynchronous requests.
3. **Request Method**: Replaced the synchronous `requests.get` call with the asynchronous `session.get` call.
4. **Response Handling**: Since `session.get` returns a `Future` object, the `.result()` method is used to retrieve the actual response.

These changes ensure that the code now uses `requests_futures` for asynchronous HTTP requests while maintaining the original functionality.

---

### Modified Code
```python
from dataclasses import dataclass
from typing import Optional
from enum import Enum, unique

from requests_futures.sessions import FuturesSession
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
    
    # Use FuturesSession for asynchronous requests
    session = FuturesSession()
    future = session.get(url)
    response = future.result()  # Wait for the response to complete

    soup = BeautifulSoup(response.text, "html.parser")

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

---

### Summary of Changes
- Replaced `requests.get` with `session.get` from `FuturesSession`.
- Used `.result()` to retrieve the response from the `Future` object.
- Ensured no other parts of the code were altered to maintain compatibility with the rest of the application.