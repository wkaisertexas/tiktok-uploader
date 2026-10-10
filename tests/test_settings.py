"""
Validation of config values that the browser flow does not exercise
"""

from pydantic import ValidationError
from pytest import raises

from tiktok_uploader.settings import Captions


def _captions(endpoint: str) -> Captions:
    return Captions.model_validate(
        {
            "endpoint": endpoint,
            "model": "test-model",
            "api_key_env": "MODEL_ACCESS_KEY",
            "min_hashtags": 1,
            "max_hashtags": 4,
            "timeout": 30,
        }
    )


def test_captions_endpoint_accepts_https() -> None:
    _captions("https://inference.do-ai.run")


def test_captions_endpoint_rejects_http() -> None:
    with raises(ValidationError, match="must use https"):
        _captions("http://inference.do-ai.run")
