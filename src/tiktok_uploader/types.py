from datetime import datetime
from http.cookiejar import Cookie as HttpCookie
from typing import Literal, TypedDict


class ProxyDict(TypedDict, total=False):
    user: str
    password: str
    host: str
    port: str


class VideoDict(TypedDict, total=False):
    path: str
    video: str
    comment: bool
    stitch: bool
    duet: bool
    reuse_of_content: bool
    description: str
    schedule: datetime
    product_id: str
    cover: str
    visibility: Literal["everyone", "friends", "only_you"]
    sound_name: str
    sound_artist: str
    draft: bool
    ai_label: bool
    skip_restricted: bool


class Cookie(TypedDict, total=False):
    name: str
    value: str
    domain: str
    path: str
    expiry: int
    expires: int
    sameSite: str


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
