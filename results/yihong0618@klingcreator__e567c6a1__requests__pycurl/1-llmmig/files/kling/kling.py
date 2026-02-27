import argparse
import os
import time
import contextlib
import io
from typing import Optional
from enum import Enum
from http.cookies import SimpleCookie

from fake_useragent import UserAgent
import pycurl
from rich import print
import threading

browser_version = "edge101"
ua = UserAgent(browsers=["edge"])
base_url = "https://klingai.kuaishou.com/"
base_url_not_cn = "https://klingai.com/"


def call_for_daily_check(curl: pycurl.Curl, is_cn: bool) -> bool:
    buffer = io.BytesIO()
    url = f"{base_url}api/pay/reward?activity=login_bonus_daily" if is_cn else f"{base_url_not_cn}api/pay/reward?activity=login_bonus_daily"
    curl.setopt(pycurl.URL, url)
    curl.setopt(pycurl.WRITEFUNCTION, buffer.write)
    curl.perform()
    status_code = curl.getinfo(pycurl.RESPONSE_CODE)
    if status_code == 200:
        response_data = buffer.getvalue().decode("utf-8")
        print(f"Call daily login success with {is_cn}:\n{response_data}\n")
        return True

    raise Exception(
        "Call daily login failed with CN or Non-CN. The token may be incorrect."
    )


class TaskStatus(Enum):
    PENDING = 0
    COMPLETED = 1
    FAILED = 3


class BaseGen:
    def __init__(self, cookie: str) -> None:
        self.curl = pycurl.Curl()
        self.cookie = cookie
        self.cookie_file = "cookies.txt"
        self.is_cn = False
        self.setup_curl()
        call_for_daily_check(self.curl, self.is_cn)

    def setup_curl(self):
        self.curl.setopt(pycurl.COOKIEFILE, self.cookie_file)
        self.curl.setopt(pycurl.COOKIEJAR, self.cookie_file)
        self.curl.setopt(pycurl.USERAGENT, ua.random)
        self.curl.setopt(pycurl.FOLLOWLOCATION, True)
        self.curl.setopt(pycurl.TIMEOUT, 30)
        self.curl.setopt(pycurl.FAILONERROR, True)
        self.parse_cookie_string(self.cookie)

    def parse_cookie_string(self, cookie_string):
        cookie = SimpleCookie()
        cookie.load(cookie_string)
        with open(self.cookie_file, "w") as f:
            for key, morsel in cookie.items():
                if key.startswith("kuaishou"):
                    self.is_cn = True
                f.write(f"{key}={morsel.value};\n")

    def get_account_point(self) -> float:
        buffer = io.BytesIO()
        self.curl.setopt(pycurl.URL, f"{base_url}api/account/point")
        self.curl.setopt(pycurl.WRITEFUNCTION, buffer.write)
        self.curl.perform()
        response_data = buffer.getvalue().decode("utf-8")
        point_data = eval(response_data)  # Assuming JSON-like response
        assert point_data.get("status") == 200
        total_point = point_data["data"]["total"]
        return total_point / 100

    def image_uploader(self, image_path) -> str:
        buffer = io.BytesIO()
        with open(image_path, "rb") as f:
            image_data = f.read()

        file_name = os.path.basename(image_path)
        upload_url = f"{base_url}api/upload/issue/token?filename={file_name}"
        self.curl.setopt(pycurl.URL, upload_url)
        self.curl.setopt(pycurl.WRITEFUNCTION, buffer.write)
        self.curl.perform()
        token_data = eval(buffer.getvalue().decode("utf-8"))  # Assuming JSON-like response
        assert token_data.get("status") == 200

        token = token_data["data"]["token"]
        resume_url = f"{base_url}api/upload/resume?upload_token={token}"
        buffer = io.BytesIO()
        self.curl.setopt(pycurl.URL, resume_url)
        self.curl.setopt(pycurl.WRITEFUNCTION, buffer.write)
        self.curl.perform()
        resume_data = eval(buffer.getvalue().decode("utf-8"))
        assert resume_data.get("result") == 1

        # Upload fragment
        buffer = io.BytesIO()
        self.curl.setopt(pycurl.URL, f"{base_url}api/upload/fragment")
        self.curl.setopt(pycurl.POST, 1)
        self.curl.setopt(pycurl.POSTFIELDS, image_data)
        self.curl.setopt(pycurl.WRITEFUNCTION, buffer.write)
        self.curl.perform()
        fragment_data = eval(buffer.getvalue().decode("utf-8"))
        assert fragment_data.get("result") == 1

        # Complete upload
        buffer = io.BytesIO()
        self.curl.setopt(pycurl.URL, f"{base_url}api/upload/complete?upload_token={token}&fragment_count=1")
        self.curl.setopt(pycurl.POST, 1)
        self.curl.setopt(pycurl.WRITEFUNCTION, buffer.write)
        self.curl.perform()
        complete_data = eval(buffer.getvalue().decode("utf-8"))
        assert complete_data.get("result") == 1

        # Verify upload
        buffer = io.BytesIO()
        self.curl.setopt(pycurl.URL, f"{base_url}api/upload/verify/token?token={token}")
        self.curl.setopt(pycurl.WRITEFUNCTION, buffer.write)
        self.curl.perform()
        result_data = eval(buffer.getvalue().decode("utf-8"))
        assert result_data.get("status") == 200
        return result_data.get("data").get("url")

    def fetch_metadata(self, task_id: str) -> tuple[dict, TaskStatus]:
        buffer = io.BytesIO()
        url = f"{base_url}api/task/status?taskId={task_id}"
        self.curl.setopt(pycurl.URL, url)
        self.curl.setopt(pycurl.WRITEFUNCTION, buffer.write)
        self.curl.perform()
        data = eval(buffer.getvalue().decode("utf-8")).get("data")
        assert data is not None
        if data.get("status") >= 90:
            return data, TaskStatus.COMPLETED
        elif data.get("status") in [9, 50]:
            return data, TaskStatus.FAILED
        else:
            return data, TaskStatus.PENDING
