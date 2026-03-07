import aiohttp
import asyncio

class Waits:
    def __init__(self, driver):
        self.driver = driver

    async def fetch_timeouts(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.driver.command_executor._url}/session/{self.driver.session_id}/timeouts") as response:
                return await response.json()

    async def initialize(self):
        response = await self.fetch_timeouts()
        self.implicit = int(response["value"]["implicit"] / 1000)
        self.page_load = int(response["value"]["pageLoad"] / 1000)
        self.script = int(response["value"]["script"] / 1000)

async def get_implicit_wait(driver):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{driver.command_executor._url}/session/{driver.session_id}/timeouts") as response:
            response_json = await response.json()
            return int(response_json["value"]["implicit"] / 1000)
