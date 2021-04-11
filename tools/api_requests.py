from flask import request
import requests


class ApiRequest:
    request_function = None

    @classmethod
    def make_request(cls, *url_parts, **kwargs):
        url = request.url_root + "api/" + "/".join(map(str, url_parts))
        headers = dict()
        access_token = request.cookies.get("access_token_cookie")
        if access_token:
            headers = {"Authorization": f"Bearer {access_token}"}
        return cls.request_function(url, headers=headers, **kwargs)


class ApiGet(ApiRequest):
    request_function = requests.get


class ApiPost(ApiRequest):
    request_function = requests.post


class ApiPut(ApiRequest):
    request_function = requests.put


class ApiDelete(ApiRequest):
    request_function = requests.delete
