"""
Rewrites a video's original title into an English TikTok caption with hashtags,
using any OpenAI-compatible chat completions endpoint
"""

import json
import logging
import os
import re
import urllib.request
from pathlib import Path

from tiktok_uploader import config

logger = logging.getLogger(__name__)

# renders are named YY-MM-DD_<11 character video id>_<title>.mp4
RENDER_PREFIX = re.compile(r"^\d{2}-\d{2}-\d{2}_[\w-]{11}_")
HASHTAG = re.compile(r"^[a-z0-9]+$")

PROMPT = """You write captions for TikTok dance videos.
Rewrite the original title below into an English caption.

Rules:
- English only: translate anything that is not English. Keep song titles and artist
  names, romanized if needed (e.g. "Whistle - BLACKPINK").
- caption: one short, natural line without hashtags, @mentions or emojis.
- Never name the dancers, performers or channels in the video, in the caption or the
  hashtags. Only the song's artist may be named.
- hashtags: {min_tags} to {max_tags} relevant, popular English hashtags, lowercase letters
  and digits only, without the # sign. Prefer the song, the artist and the dance style
  over generic tags.
- The caption plus the hashtags must fit in {max_length} characters.

Reply with only JSON: {{"caption": "...", "hashtags": ["...", "..."]}}

Original title: {title}"""


class CaptionError(Exception):
    pass


def source_title(video_path: str) -> str:
    """
    The original title of a video: the sidecar <video>.txt if there is one,
    otherwise the filename without the render prefix
    """
    path = Path(video_path)
    sidecar = path.with_suffix(".txt")
    if sidecar.exists():
        title = sidecar.read_text(encoding="utf-8").strip()
        if title:
            return title

    return RENDER_PREFIX.sub("", path.stem).replace("_", " ").strip()


def rewrite_caption(title: str) -> str:
    """
    Asks the configured model for an English caption and hashtags for `title`
    """
    settings = config.captions
    api_key = os.environ.get(settings.api_key_env, "").strip()
    # MCP hosts pass an unresolved "${VAR}" placeholder through when the key is unset
    if not api_key or api_key.startswith("${"):
        raise CaptionError(f"${settings.api_key_env} is not set")

    prompt = PROMPT.format(
        title=title,
        min_tags=settings.min_hashtags,
        max_tags=settings.max_hashtags,
        max_length=config.max_description_length,
    )
    body = json.dumps(
        {
            "model": settings.model,
            "messages": [{"role": "user", "content": prompt}],
            # the model reasons before answering, which counts against this limit
            "max_tokens": 1500,
        }
    ).encode()
    request = urllib.request.Request(
        str(settings.endpoint),
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )

    # the endpoint occasionally answers with an empty message, so ask twice
    error = CaptionError("no attempts made")
    for _ in range(2):
        try:
            with urllib.request.urlopen(request, timeout=settings.timeout) as response:
                message = json.load(response)["choices"][0]["message"]
        except Exception as e:
            raise CaptionError(f"caption request failed: {e}") from e

        try:
            return _parse_reply(message.get("content") or "")
        except CaptionError as e:
            error = CaptionError(f"{e} (refusal: {message.get('refusal')})")
    raise error


def _parse_reply(reply: str) -> str:
    """
    Turns the model's JSON reply into "caption #tag1 #tag2"
    """
    match = re.search(r"\{.*\}", reply, re.DOTALL)
    if not match:
        raise CaptionError(f"model did not return JSON: {reply[:200]}")
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError as e:
        raise CaptionError(f"model returned invalid JSON: {reply[:200]}") from e

    caption = str(data.get("caption", "")).strip()
    if not caption:
        raise CaptionError("model returned an empty caption")

    hashtags = []
    for tag in data.get("hashtags", []):
        tag = str(tag).strip().lstrip("#").lower()
        if HASHTAG.match(tag) and tag not in hashtags:
            hashtags.append(tag)
    hashtags = hashtags[: config.captions.max_hashtags]

    # drop trailing hashtags rather than cut the caption mid-word
    while hashtags and len(_join(caption, hashtags)) > config.max_description_length:
        hashtags.pop()

    return _join(caption, hashtags)


def _join(caption: str, hashtags: list[str]) -> str:
    return " ".join([caption, *(f"#{tag}" for tag in hashtags)])


def auto_caption(video_path: str) -> str:
    """
    An English caption for the video, falling back to its original title if the
    model can not be reached
    """
    title = source_title(video_path)
    try:
        caption = rewrite_caption(title)
        logger.debug("Generated caption: %s", caption)
        return caption
    except CaptionError as e:
        logger.warning("Could not generate a caption (%s), using the original title", e)
        return title
