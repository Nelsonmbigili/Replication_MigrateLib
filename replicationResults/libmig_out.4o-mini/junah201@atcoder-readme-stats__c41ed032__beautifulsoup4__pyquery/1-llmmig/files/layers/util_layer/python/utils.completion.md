### Explanation of Changes
To migrate the code from using the `beautifulsoup4` library to the `pyquery` library, the following changes were made:

1. **Import Statement**: The import for `BeautifulSoup` was replaced with `from pyquery import PyQuery as pq`.
2. **Parsing HTML**: The `BeautifulSoup` object was replaced with a `PyQuery` object. Instead of using `soup.select_one()` and `soup.select()`, the equivalent `pq` methods were used: `pq('selector')` for selecting elements and `pq('selector').text` for getting text content.
3. **HTML Structure Access**: The way to access elements and their text content was adjusted to fit the `pyquery` syntax.

### Modified Code
Here is the complete code after migration to `pyquery`:

```python
from dataclasses import dataclass
from typing import Optional
from enum import Enum, unique

import requests
from pyquery import PyQuery as pq


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
    response = requests.get(url)

    doc = pq(response.text)

    # user not found
    if doc("div.alert.alert-danger").length > 0:
        return None

    user_data = doc("table.dl-table.mt-2 > tr")

    # user is unrated
    if user_data.length == 0:
        return UserData(username, "Unrated", 0, 0, "Unrated", 0)

    rank = user_data.eq(0).find("td").text()
    rating = int(user_data.eq(1).find("td > span").text())
    highest_rating = int(user_data.eq(2).find("td > span").text())
    matches = int(user_data.eq(3).find("td").text())
    tier = user_data.eq(2).find("td > span.bold").text()

    return UserData(username, rank, rating, highest_rating, tier, matches)
```