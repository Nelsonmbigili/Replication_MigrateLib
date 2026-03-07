### Changes Made

1. **Import Statement**: Changed the import from `aiohttp` to `httpx`.
2. **Request Method**: Replaced `aiohttp.request` with `httpx.AsyncClient().get` and `httpx.AsyncClient().post` for making GET and POST requests.
3. **Context Manager**: Used `async with httpx.AsyncClient() as client:` to create an HTTP client session for making requests.
4. **Response Handling**: The response handling remains the same, but now it uses the `httpx` response object.

### Modified Code
```python
import base64, qrcode, io, httpx, asyncio
from nonebot import on_command
from nonebot.rule import to_me
from nonebot.permission import GROUP_ADMIN, GROUP_OWNER, PRIVATE_FRIEND, SUPERUSER
from nonebot.adapters.cqhttp import Bot, Event
from urllib.parse import urlsplit


login = on_command('登录', rule=to_me(), permission=SUPERUSER, 
    priority=5)

@login.handle()
async def _(bot: Bot, event: Event, state: dict):
    user = User()
    qr = await user.login()
    await login.send(qr)
    while True:
        if await user.login_check():
            await user.get_cookies()
            await login.send(str(user.cookies))
            break
        await asyncio.sleep(3)

class User():
    def __init__(self):
        self.DEFAULT_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/\
            537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36",
        "Referer": "https://www.bilibili.com/"
    }

    async def get(self, url):
        async with httpx.AsyncClient() as client:
            resp = await client.get(url=url, headers=self.DEFAULT_HEADERS)
            return resp.json()

    async def post(self, url, data=''):
        async with httpx.AsyncClient() as client:
            resp = await client.post(url=url, headers=self.DEFAULT_HEADERS, data=data)
            return resp.json()

    async def login(self):
        get_login_url = 'https://passport.bilibili.com/qrcode/getLoginUrl'
        resp = await self.get(get_login_url)
        login_url = resp['data']['url']
        self.key = resp['data']['oauthKey']

        qr = qrcode.QRCode()
        qr.add_data(login_url)
        img = qr.make_image()

        buf = io.BytesIO()
        img.save(buf, format='PNG')
        heximage = base64.b64encode(buf.getvalue())
        self.qrb64 = f'[CQ:image,file=base64://{heximage.decode()}]'
        return self.qrb64

    async def login_check(self):
        get_login_info = 'http://passport.bilibili.com/qrcode/getLoginInfo'
        data = {'oauthKey': self.key}
        resp = await self.post(get_login_info, data=data)

        if resp['status']:
            self.url = resp['data']['url']
            return True
        return False
    
    async def get_cookies(self):
        query = urlsplit(self.url).query
        cookies = {}
        for s in query.split('&'):
            key, value = s.split('=')
            cookies[key] = value
        self.cookies = cookies
        return self.cookies
        return True

if __name__ == "__main__":
    async def main():
        user = User()
        qrimg = await user.login()
        print(qrimg)
        while True:
            if await user.login_check():
                print(user.cookies)
                break
            await asyncio.sleep(3)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
```