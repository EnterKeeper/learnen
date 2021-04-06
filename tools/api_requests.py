from flask import request
from requests import get, post, put, delete


def get_api_url(url_parts):
    url = request.url_root + "api"
    for part in url_parts:
        url += "/" + str(part)
    return url


def api_get(*url_parts, json=None):
    return get(get_api_url(url_parts), json=json)


def api_post(*url_parts, json=None):
    return post(get_api_url(url_parts), json=json)


def api_put(*url_parts, json=None):
    return put(get_api_url(url_parts), json=json)


def api_delete(*url_parts, json=None):
    return delete(get_api_url(url_parts), json=json)
