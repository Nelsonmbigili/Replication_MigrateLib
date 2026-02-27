import argparse
import os
import time
import contextlib
from typing import Optional
from enum import Enum
from http.cookies import SimpleCookie

from fake_useragent import UserAgent
import httpx
from rich import print
import threading

browser_version = "edge101"
ua = UserAgent(browsers=["edge"])
base_url = "https://klingai.kuaishou.com/"
base_url_not_cn = "https://klingai.com/"


def call_for_daily_check(client: httpx.Client, is_cn: bool) -> bool:
    if is_cn:
        r = client.get(f"{base_url}api/pay/reward?activity=login_bonus_daily")
    else:
        r = client.get(f"{base_url_not_cn}api/pay/reward?activity=login_bonus_daily")
    if r.status_code == 200:
        print(f"Call daily login success with {is_cn}:\n{r.json()}\n")
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
        self.client: httpx.Client = httpx.Client()
        self.cookie = cookie
        self.client.cookies, is_cn = self.parse_cookie_string(self.cookie)
        self.client.headers["user-agent"] = ua.random
        # check the daily login
        call_for_daily_check(self.client, is_cn)
        if is_cn:
            self.base_url = base_url
            image_upload_base_url = "https://upload.kuaishouzt.com/"
        else:
            self.base_url = base_url_not_cn
            image_upload_base_url = "https://upload.uvfuns.com/"

        self.apis_dict = {
            "image_upload_gettoken": f"{self.base_url}api/upload/issue/token?filename=",
            "image_upload_resume": f"{image_upload_base_url}api/upload/resume?upload_token=",
            "image_upload_fragment": f"{image_upload_base_url}api/upload/fragment",
            "image_upload_complete": f"{image_upload_base_url}api/upload/complete",
            "image_upload_geturl": f"{self.base_url}api/upload/verify/token?token=",
        }

        self.submit_url = f"{self.base_url}api/task/submit"
        self.daily_url = f"{self.base_url}api/pay/reward?activity=login_bonus_daily"
        self.point_url = f"{self.base_url}api/account/point"
        # store the video id list maybe for future use or extend
        self.video_id_list = []

    @staticmethod
    def parse_cookie_string(cookie_string):
        cookie = SimpleCookie()
        cookie.load(cookie_string)
        cookies_dict = {}
        is_cn = False
        for key, morsel in cookie.items():
            if key.startswith("kuaishou"):
                is_cn = True
            cookies_dict[key] = morsel.value
        return cookies_dict, is_cn

    def get_account_point(self) -> float:
        bonus_req = self.client.get(self.daily_url)
        bonus_data = bonus_req.json()
        assert bonus_data.get("status") == 200

        point_req = self.client.get(self.point_url)
        point_data = point_req.json()
        assert point_data.get("status") == 200

        total_point = point_data["data"]["total"]
        return total_point / 100

    def image_uploader(self, image_path) -> str:
        with open(image_path, "rb") as f:
            image_data = f.read()
        # get the image file name
        file_name = image_path.split("/")[-1]
        upload_url = self.apis_dict["image_upload_gettoken"] + file_name
        token_req = self.client.get(upload_url)
        token_data = token_req.json()

        assert token_data.get("status") == 200

        token = token_data["data"]["token"]
        resume_url = self.apis_dict["image_upload_resume"] + token
        resume_req = self.client.get(resume_url)
        resume_data = resume_req.json()

        assert resume_data.get("result") == 1
        fragment_req = self.client.post(
            self.apis_dict["image_upload_fragment"],
            data=image_data,
            params=dict(upload_token=token, fragment_id=0),
            headers={"Content-Type": "application/octet-stream"},
        )
        fragment_data = fragment_req.json()
        assert fragment_data.get("result") == 1
        complete_req = self.client.post(
            self.apis_dict["image_upload_complete"],
            params=dict(upload_token=token, fragment_count=1),
        )
        complete_data = complete_req.json()
        assert complete_data.get("result") == 1
        verify_url = self.apis_dict["image_upload_geturl"] + token
        result_req = self.client.get(verify_url)
        result_data = result_req.json()
        assert result_data.get("status") == 200
        return result_data.get("data").get("url")

    def fetch_metadata(self, task_id: str) -> tuple[dict, TaskStatus]:
        url = f"{self.base_url}api/task/status?taskId={task_id}"
        response = self.client.get(url)
        data = response.json().get("data")
        assert data is not None
        if data.get("status") >= 90:
            return data, TaskStatus.COMPLETED
        elif data.get("status") in [9, 50]:
            return data, TaskStatus.FAILED
        else:
            return data, TaskStatus.PENDING


class VideoGen(BaseGen):
    # The rest of the VideoGen class remains unchanged
    ...


class ImageGen(BaseGen):
    # The rest of the ImageGen class remains unchanged
    ...


def main():
    # The main function remains unchanged
    ...


if __name__ == "__main__":
    main()
