import requests

class Waits:
    def __init__(self, driver):
        response = requests.get(
            f"{driver.command_executor._url}/session/{driver.session_id}/timeouts"
        ).json()
        self.implicit = int(response["value"]["implicit"] / 1000)
        self.page_load = int(response["value"]["pageLoad"] / 1000)
        self.script = int(response["value"]["script"] / 1000)


def get_implicit_wait(driver):
    response = requests.get(
        f"{driver.command_executor._url}/session/{driver.session_id}/timeouts"
    ).json()
    return int(response["value"]["implicit"] / 1000)
