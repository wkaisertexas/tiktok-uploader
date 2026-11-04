from enum import Enum
from pathlib import Path
from typing import Annotated

import toml
from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")  # reject unknown keys


class VisibilityOption(str, Enum):
    Public = "Public"
    Friends = "Friends"
    Private = "Private"


PositiveSeconds = Annotated[int, Field(ge=0)]
PositiveChars = Annotated[int, Field(ge=1)]


class Paths(StrictModel):
    main: HttpUrl
    login: HttpUrl
    upload: HttpUrl


class Disguising(StrictModel):
    user_agent: str

    @field_validator("user_agent")
    @classmethod
    def _ua_nonempty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("user_agent must be non-empty")
        return v


class CookiesBanner(StrictModel):
    banner: str
    button: str


class LoginSelectors(StrictModel):
    username_field: str
    password_field: str
    login_button: str
    alert_user_if_failed: bool
    cookie_of_interest: str


class Cover(StrictModel):
    cover_preview: str
    edit_cover_button: str
    edit_cover_container: str
    upload_cover_tab: str
    upload_cover: str
    upload_confirmation: str
    exit_cover_container: str
    # TikTok Studio's cover modal (tried first, the legacy flow above is the fallback)
    studio_edit_cover: str
    studio_upload_cover: str
    studio_save: str
    studio_cancel: str


class SoundSelectors(StrictModel):
    add_sound_button: str
    search_input: str
    result_items: str
    result_title: str
    result_artist: str
    result_add_button: str
    save_button: str


class UploadSelectors(StrictModel):
    iframe: str
    split_window: str
    modal_dismiss: str
    modal_overlay: str
    show_more: str
    upload_video: str
    upload_finished: str
    upload_confirmation: str
    process_confirmation: str
    description: str
    cover: Cover
    sound: SoundSelectors

    visibility: str
    options: list[VisibilityOption]

    mention_box: str
    mention_box_user_id: str

    comment: str
    reuse_of_content: str
    duet: str
    stitch: str

    ai_label_switch: str
    ai_label_confirm: str
    content_restricted: str

    post: str
    post_now: str
    post_confirmation: str
    post_error: str
    save_draft: str

    cookies_banner: CookiesBanner


class ScheduleSelectors(StrictModel):
    switch: str
    consent_allow: str

    date_picker: str
    date_picker_text: str
    calendar: str
    calendar_month: str
    calendar_year: str
    calendar_valid_days: str
    calendar_arrows: str

    time_picker: str
    time_picker_text: str
    time_picker_container: str
    timepicker_hour: str  # {value} is zero-padded: "09"
    timepicker_minute: str


class Selectors(StrictModel):
    login: LoginSelectors
    upload: UploadSelectors
    schedule: ScheduleSelectors


class TikTokConfig(StrictModel):
    # Booleans
    headless: bool
    quit_on_end: bool

    # Lists of accepted input aliases
    valid_path_names: list[str]
    valid_descriptions: list[str]

    # Waits (seconds)
    implicit_wait: PositiveSeconds
    explicit_wait: PositiveSeconds
    uploading_wait: PositiveSeconds
    add_hashtag_wait: PositiveSeconds

    # Files / text
    supported_file_types: list[str]
    supported_image_file_types: list[str]
    max_description_length: PositiveChars

    # Nested
    paths: Paths
    disguising: Disguising
    selectors: Selectors

    @field_validator("valid_path_names", "valid_descriptions")
    @classmethod
    def _nonempty_unique(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("list must be non-empty")
        stripped = [s.strip() for s in v]
        if any(not s for s in stripped):
            raise ValueError("list entries must be non-empty strings")
        if len(set(map(str.lower, stripped))) != len(stripped):
            raise ValueError("list entries must be unique (case-insensitive)")
        return stripped

    @field_validator("supported_file_types", "supported_image_file_types")
    @classmethod
    def _extensions(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("supported_file_types must be non-empty")
        for ext in v:
            if not ext or any(ch in ext for ch in ". /\\"):
                raise ValueError(f"invalid file extension: {ext!r}")
            if ext.lower() != ext:
                raise ValueError(f"file extensions must be lowercase: {ext!r}")
        if len(set(v)) != len(v):
            raise ValueError("supported_file_types must be unique")
        return v


def load_config(path: str | Path) -> TikTokConfig:
    """
    Load and validate a TOML config file into a TikTokConfig.
    Raises pydantic.ValidationError on any mismatch.
    """
    p = Path(path)
    data = toml.load(p)
    return TikTokConfig.model_validate(data)
