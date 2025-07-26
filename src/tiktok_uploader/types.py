from typing import TypedDict

from datetime import datetime
from http.cookiejar import Cookie as HttpCookie


class ProxyDict(TypedDict, total=False):
    user: str
    password: str
    host: str
    port: str


class VideoDict(TypedDict, total=False):
    path: str
    video: str
    stitch: bool
    duel: bool
    description: str
    schedule: datetime
    product_id: str


class Cookie(TypedDict, total=False):
    name: str
    value: str
    domain: str
    path: str
    expiry: int


def cookie_from_dict(data: Cookie) -> HttpCookie:
    return HttpCookie(
        0,
        data["name"],
        data["value"],
        None,
        False,
        data.get("domain", ""),
        bool(data.get("domain")),
        data.get("domain", "").startswith("."),
        data.get("path", "/"),
        bool(data.get("path")),
        False,
        data.get("expiry"),
        False,
        None,
        None,
        {},
        False,
    )
