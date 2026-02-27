import httpx

class Waits:
    def __init__(self, driver):
        url = f"{driver.command_executor._url}/session/{driver.session_id}/timeouts"
        response = httpx.get(url)
        response_data = response.json()
        self.implicit = int(response_data["value"]["implicit"] / 1000)
        self.page_load = int(response_data["value"]["pageLoad"] / 1000)
        self.script = int(response_data["value"]["script"] / 1000)


def get_implicit_wait(driver):
    url = f"{driver.command_executor._url}/session/{driver.session_id}/timeouts"
    response = httpx.get(url)
    response_data = response.json()
    return int(response_data["value"]["implicit"] / 1000)
