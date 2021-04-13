import os

from flask import url_for


def get_avatar(filename):
    path = url_for("static", filename="avatars")
    files = os.listdir(path[1:])
    if filename not in files:
        filename = "default"
    return path + "/" + filename + ".png"
