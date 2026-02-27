import aiohttp
import asyncio

class Waits:
    async def __init__(self, driver):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{driver.command_executor._url}/session/{driver.session_id}/timeouts"
            ) as response:
                response_data = await response.json()
                self.implicit = int(response_data["value"]["implicit"] / 1000)
                self.page_load = int(response_data["value"]["pageLoad"] / 1000)
                self.script = int(response_data["value"]["script"] / 1000)


async def get_implicit_wait(driver):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{driver.command_executor._url}/session/{driver.session_id}/timeouts"
        ) as response:
            response_data = await response.json()
            return int(response_data["value"]["implicit"] / 1000)
