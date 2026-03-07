### Explanation of Changes

To migrate the code from using the `requests` library to the `pycurl` library, the following changes were made:

1. **Importing PyCurl**: The `requests` library was replaced with `pycurl`.
2. **Making HTTP Requests**: The `requests.get()` method was replaced with a `pycurl` setup that initializes a cURL object, sets the necessary options, and performs the request.
3. **Handling Response**: The response from `pycurl` is handled differently than `requests`. The response data is captured using a callback function that writes the data to a buffer.
4. **Error Handling**: The error handling for HTTP errors was adapted to check the HTTP response code after the request is made, as `pycurl` does not raise exceptions for HTTP errors like `requests` does.

Here is the modified code:

```python
import json
import unittest
from collections.abc import MutableMapping, Sequence, Mapping
from typing import Any
import pycurl
from io import BytesIO
from horde_sdk.ai_horde_api.apimodels import ImageGenerateAsyncRequest, ImageGenerationInputPayload


def get_github_json_file(url: str) -> dict[str, Any]:
    buffer = BytesIO()
    curl = pycurl.Curl()
    curl.setopt(curl.URL, url)
    curl.setopt(curl.HTTPHEADER, ["Accept: application/vnd.github.raw+json"])
    curl.setopt(curl.WRITEDATA, buffer)
    curl.perform()
    
    # Check for HTTP errors
    http_code = curl.getinfo(curl.RESPONSE_CODE)
    curl.close()
    if http_code != 200:
        raise Exception(f"HTTP error: {http_code}")

    response_data = buffer.getvalue()
    return json.loads(response_data)


def recursive_update(target: MutableMapping[str, Any], source: Mapping[str, Any]) -> None:
    for key, value in source.items():
        if isinstance(value, MutableMapping):
            recursive_update(target.setdefault(key, {}), value)
        elif isinstance(value, Sequence):
            target.setdefault(key, []).extend(value)
        else:
            target[key] = value


class TestStyles(unittest.TestCase):
    def setUp(self):
        with open("styles.json", "r", encoding="utf-8") as file:
            self.styles: dict[str, dict[str, Any]] = json.load(file)
        with open("enhancements.json", "r", encoding="utf-8") as file:
            self.enhancements: dict[str, dict[str, Any]] = json.load(file)
        self.model_reference: dict[str, dict[str, Any]] = get_github_json_file(
            "https://api.github.com/repos/Haidra-Org/AI-Horde-image-model-reference/contents/stable_diffusion.json"
        )

    @staticmethod
    def validate_request(request: dict[str, ImageGenerationInputPayload | Any]) -> None:
        ImageGenerateAsyncRequest.model_validate(request, strict=True)

    def style_to_request(self, style: dict[str, Any]) -> dict[str, ImageGenerationInputPayload | Any]:
        with self.subTest(msg="Validate model exists"):
            model = style.get("model")
            if model is not None:
                self.assertIn(model, self.model_reference, msg=f"Model {model} does not exist for style {style}")

        with self.subTest(msg="Validate prompt"):
            prompt = style.pop("prompt")
            if "###" not in prompt and "{np}" in prompt:
                prompt = prompt.replace("{np}", "###{np}")

            # The negative prompt is greedy
            positive_prompt, *negative_prompt = prompt.split("###")
            negative_prompt = "###".join(negative_prompt) or None
            del prompt

            self.assertIn("{p}", positive_prompt, msg="Positive prompt must contain {p}")
            self.assertNotIn("{np}", positive_prompt, msg="Positive prompt must not contain {np}")
            if negative_prompt is not None:
                self.assertIn("{np}", negative_prompt, msg="Negative prompt must contain {np}")
                self.assertNotIn("{p}", negative_prompt, msg="Negative prompt must not contain {p}")

        request = {
            "prompt": positive_prompt + (f"###{negative_prompt}" if negative_prompt else ""),
            "params": {},
        }
        if style.pop("enhance", False):
            with self.subTest(msg="Validate enhancement"):
                model = style["model"]
                baseline = self.model_reference[model]["baseline"]
                enhancements = self.enhancements[baseline]
                recursive_update(style, enhancements)
        if "model" in style:
            request["models"] = [style.pop("model")]

        with self.subTest(msg="Convert to request"):
            request_fields = set(ImageGenerateAsyncRequest.model_fields.keys())
            params_fields = set(ImageGenerationInputPayload.model_fields.keys())
            for field, value in style.items():
                if field in params_fields:
                    request["params"][field] = value
                elif field in request_fields:
                    request[field] = value
                else:
                    raise KeyError(f"Unknown field: {field}")

        if not request["params"]:
            del request["params"]

        return request

    def test_enhancements(self) -> None:
        base_request = {
            "prompt": "{p}",
            "models": [],
        }
        for enhancement_name, enhancement in self.enhancements.items():
            with self.subTest(enhancement=enhancement_name):
                request = self.style_to_request(base_request | enhancement)
                self.validate_request(request)

    def test_styles(self) -> None:
        for style_name, style in self.styles.items():
            with self.subTest(style=style_name):
                request = self.style_to_request(style)
                self.validate_request(request)
``` 

This code now uses `pycurl` for making HTTP requests instead of `requests`, while keeping the overall structure and logic intact.