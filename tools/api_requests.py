from flask import request
from requests import get, post, put, delete


class ApiRequest:
    request_function = None

    @classmethod
    def make_request(cls, url_parts, **kwargs):
        url = request.url_root + "api/" + "/".join(map(str, url_parts))
        return cls.request_function(url, **kwargs)


class ApiGet(ApiRequest):
    request_function = get


class ApiPost(ApiRequest):
    request_function = post


class ApiPut(ApiRequest):
    request_function = put


class ApiDelete(ApiRequest):
    request_function = delete
