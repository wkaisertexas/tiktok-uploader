"""
The schedule selectors: the switch was a literal id ("tux-1") that stopped
matching once TikTok Studio moved to "Now" / "Schedule" radios with
session-random ids (#201, #212, #224).
"""

from tiktok_uploader import config


def test_schedule_switch_selector_is_not_the_stale_literal_id() -> None:
    assert "tux-1" not in config.selectors.schedule.switch


def test_schedule_switch_selector_targets_the_schedule_radio_by_label_text() -> None:
    selector = config.selectors.schedule.switch
    assert "Radio__root" in selector
    assert "Schedule" in selector


def test_schedule_consent_allow_selector_is_configured() -> None:
    """TikTok's 'Allow your video to be saved for scheduled posting?'
    dialog, shown after the Schedule radio, needs its own selector."""
    assert "Allow" in config.selectors.schedule.consent_allow


def test_date_and_time_pickers_are_selected_by_aria_label_not_position() -> None:
    """Studio renders the date and time as ARIA comboboxes ("Select date" /
    "Select time"); the TUXFormField inputs and "date-picker-input" divs are
    gone."""
    sched = config.selectors.schedule
    assert "Select date" in sched.date_picker
    assert "Select time" in sched.time_picker
    assert sched.date_picker != sched.time_picker
    for stale in ("TUXFormField", "date-picker-input", "time-picker-input"):
        assert stale not in sched.date_picker + sched.time_picker


def test_calendar_selectors_do_not_pin_a_generated_class() -> None:
    sched = config.selectors.schedule
    assert "jsx-" not in sched.calendar_valid_days
    assert "data-disabled='false'" in sched.calendar_valid_days
    assert "data-outside='false'" in sched.calendar_valid_days
    assert "DatePicker__titleMonth" in sched.calendar_month
    assert "DatePicker__titleYear" in sched.calendar_year


def test_time_options_are_picked_by_their_label() -> None:
    sched = config.selectors.schedule
    assert sched.timepicker_hour.format(value="09").endswith("@aria-label='Hours 09']")
    assert sched.timepicker_minute.format(value="05").endswith(
        "@aria-label='Minutes 05']"
    )
    assert sched.time_picker_container.count("@class=") == 0
