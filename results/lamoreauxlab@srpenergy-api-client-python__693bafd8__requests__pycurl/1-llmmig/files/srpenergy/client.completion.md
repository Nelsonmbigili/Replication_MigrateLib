### Explanation of Changes
To migrate the code from the `requests` library to the `pycurl` library, the following changes were made:
1. **Session Management**: `pycurl` does not have a session object like `requests.Session`. Instead, we use a `pycurl.Curl` object to handle individual HTTP requests.
2. **HTTP Methods**: `pycurl` requires explicit configuration for HTTP methods (e.g., `POST`, `GET`) and headers. These are set using options like `pycurl.POSTFIELDS` for POST data and `pycurl.HTTPHEADER` for headers.
3. **Response Handling**: `pycurl` writes the response to a buffer, which must be read and decoded manually. This replaces the `response.json()` and `response.cookies` functionality in `requests`.
4. **Cookie Management**: Cookies are handled using `pycurl.COOKIEFILE` and `pycurl.COOKIEJAR` to persist cookies across requests.
5. **Error Handling**: `pycurl` raises exceptions for HTTP errors, which are caught and handled similarly to `requests`.

Below is the modified code with the necessary changes.

---

### Modified Code
```python
import pycurl
from io import BytesIO
from urllib.parse import urlencode, unquote

class SrpEnergyClient:
    """SrpEnergyClient(accountid, username, password).

    Client used to fetch srp energy usage.

    Parameters
    ----------
    accountid : string
        An srp account id.
    username: string
        An srp account username.
    password: string
        An srp account password

    Methods
    -------
    validate()
        Validate user credentials.
    usage(startdate, enddate)
        Get the usage for a given date range.

    """

    def __init__(self, accountid, username, password):  # noqa: D107

        # Validate parameters
        if accountid is None:
            raise TypeError("Parameter account can not be none.")

        if username is None:
            raise TypeError("Parameter username can not be none.")

        if password is None:
            raise TypeError("Parameter password can not be none.")

        if not accountid:
            raise ValueError("Parameter accountid must have length greater than 0.")

        if not username:
            raise ValueError("Parameter username must have length greater than 0.")

        if not password:
            raise ValueError("Parameter password must have length greater than 0.")

        if not re.match(r"^\d{9}$", accountid):
            raise ValueError("Parameter account should only contain numbers.")

        self.accountid = accountid
        self.username = username
        self.password = password

    def _make_request(self, url, method="GET", data=None, headers=None, cookies=None):
        """Helper function to make HTTP requests using pycurl."""
        buffer = BytesIO()
        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, url)
        curl.setopt(pycurl.WRITEDATA, buffer)

        if method == "POST":
            curl.setopt(pycurl.POST, 1)
            if data:
                curl.setopt(pycurl.POSTFIELDS, urlencode(data))

        if headers:
            curl.setopt(pycurl.HTTPHEADER, headers)

        if cookies:
            curl.setopt(pycurl.COOKIEFILE, cookies)
            curl.setopt(pycurl.COOKIEJAR, cookies)

        try:
            curl.perform()
            response_code = curl.getinfo(pycurl.RESPONSE_CODE)
            if response_code != 200:
                raise Exception(f"HTTP request failed with status code {response_code}")
        finally:
            curl.close()

        return buffer.getvalue().decode("utf-8")

    def validate(self):
        """Validate user credentials.

        Returns
        -------
        bool

        """
        try:
            # Login request
            response = self._make_request(
                BASE_USAGE_URL + "/login/authorize",
                method="POST",
                data={"username": self.username, "password": self.password},
            )
            data = json.loads(response)
            valid = data["message"] == "Log in successful."
            return valid

        except Exception:  # pylint: disable=W0703
            return False

    def usage(self, startdate, enddate, is_tou=False):  # pylint: disable=R0914
        """Get the energy usage for a given date range.

        Parameters
        ----------
        startdate : datetime
            the start date
        enddate : datetime
            the end date
        is_tou : bool
            indicate if usage is a time of use plan

        Returns
        -------
        list of tuple
            In the form of (datepart, timepart, isotime, kw, cost)

        """
        # Validate parameters
        if not isinstance(startdate, datetime):
            raise ValueError("Parameter startdate must be datetime.")

        if not isinstance(enddate, datetime):
            raise ValueError("Parameter enddate must be datetime.")

        # Validate date ranges
        if startdate > enddate:
            raise ValueError("Parameter startdate can not be greater than enddate.")

        # Validate date ranges
        if startdate.timestamp() > datetime.now().timestamp():
            raise ValueError("Parameter startdate can not be greater than now.")

        try:
            # Convert datetime to strings
            str_startdate = startdate.strftime("%m-%d-%Y")
            str_enddate = enddate.strftime("%m-%d-%Y")

            # Login and get antiforgery token
            cookies_file = "cookies.txt"
            self._make_request(
                BASE_USAGE_URL + "login/authorize",
                method="POST",
                data={"username": self.username, "password": self.password},
                cookies=cookies_file,
            )

            response = self._make_request(
                BASE_USAGE_URL + "login/antiforgerytoken", cookies=cookies_file
            )
            xsrf_token = unquote(json.loads(response)["xsrf-token"])

            # Fetch usage data
            response = self._make_request(
                BASE_USAGE_URL
                + "usage/hourlydetail?billaccount="
                + self.accountid
                + "&beginDate="
                + str_startdate
                + "&endDate="
                + str_enddate,
                headers={"x-xsrf-token": xsrf_token},
                cookies=cookies_file,
            )

            data = json.loads(response)
            hourly_usage_list = data["hourlyUsageList"]

            usage = []
            for row in hourly_usage_list:

                total_kwh = row["totalKwh"]
                if total_kwh == 0:
                    # Build the total_kwh from separate fields for EZ-3.
                    total_kwh = (
                        row["onPeakKwh"]
                        + row["offPeakKwh"]
                        + row["shoulderKwh"]
                        + row["superOffPeakKwh"]
                    )

                total_cost = row["totalCost"]
                if total_cost == 0:
                    # Build the total_cost from separate fields for EZ-3.
                    total_cost = (
                        row["onPeakCost"]
                        + row["offPeakCost"]
                        + row["shoulderCost"]
                        + row["superOffPeakCost"]
                    )

                # Check if on Time of Use Plan
                if is_tou:

                    rate, is_peak = get_rate(row["date"])

                    if is_peak:
                        total_kwh = row["onPeakKwh"]
                    else:
                        total_kwh = row["offPeakKwh"]

                    total_cost = total_kwh * rate

                values = (
                    get_pretty_date(row["date"]),
                    get_pretty_time(row["date"]),
                    row["date"],
                    total_kwh,
                    round(total_cost, 2),
                )
                usage.append(values)

            return usage

        except Exception as ex:
            raise ex
```

---

### Key Notes
- The `pycurl` library requires more manual handling of HTTP requests compared to `requests`.
- Cookies are managed using a file (`cookies.txt`) to persist them across requests.
- The response is read from a buffer and decoded manually.
- The overall structure and logic of the code remain unchanged to ensure compatibility with the rest of the application.