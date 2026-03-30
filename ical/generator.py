from datetime import datetime, timezone, date, timedelta
from typing import List, Dict
from icalendar import Calendar, Event
from uuid import uuid4
import os
import re

# Map known tag_type_codes to human-readable names with emoji
TAG_LABELS = {
    "tag_generic_caffeine": "☕ Caffeine",
    "tag_generic_alcohol": "🍷 Alcohol",
    "tag_generic_late_meal": "🍽️ Late Meal",
    "tag_generic_stressful_day": "😰 Stressful Day",
    "tag_generic_workout": "🏋️ Workout",
    "tag_generic_outdoor_time": "🌳 Outdoor Time",
    "tag_generic_meditation": "🧘 Meditation",
    "tag_generic_nap": "😴 Nap",
    "tag_generic_screen_time": "📱 Screen Time",
    "tag_generic_sick": "🤒 Sick",
    "tag_generic_relaxation": "🛀 Relaxation",
    "tag_generic_reading": "📖 Reading",
    "tag_generic_sauna": "🧖 Sauna",
    "tag_generic_cold_exposure": "🥶 Cold Exposure",
    "tag_generic_breathwork": "🌬️ Breathwork",
    "tag_generic_journal": "📓 Journal",
    "tag_generic_supplement": "💊 Supplement",
    "tag_generic_hydration": "💧 Hydration",
    "tag_generic_early_meal": "🌅 Early Meal",
    "tag_generic_big_meal": "🍔 Big Meal",
    "tag_generic_light_meal": "🥗 Light Meal",
    "tag_generic_no_alcohol": "🚫🍷 No Alcohol",
    "tag_generic_no_caffeine": "🚫☕ No Caffeine",
    "tag_generic_airplane": "✈️ Airplane",
    "tag_generic_beer": "🍺 Beer",
    "tag_generic_coffee": "☕ Coffee",
    "tag_generic_wine": "🍷 Wine",
    "tag_sleep_alcohol": "🍷 Alcohol (Sleep)",
    "tag_sleep_sauna": "🧖 Sauna (Sleep)",
}

# Regex to detect UUID-style tag_type_codes (custom tags)
_UUID_PATTERN = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)

def format_tag_label(tag: Dict, custom_tag_names: dict = None) -> str:
    """Convert a tag to a human-readable label."""
    tag_code = tag.get("tag_type_code", "")

    # Check known labels
    if tag_code in TAG_LABELS:
        return TAG_LABELS[tag_code]

    # Check user-configured custom tag names (value used as-is, include your own icon)
    if custom_tag_names and tag_code in custom_tag_names:
        return custom_tag_names[tag_code]

    # Use custom_name from API if available
    custom_name = tag.get("custom_name")
    if custom_name:
        return f"🏷️ {custom_name}"

    # For UUID-style codes, show as unknown custom tag
    if _UUID_PATTERN.match(tag_code):
        return f"🏷️ Custom Tag ({tag_code[:8]})"

    # Fall back to cleaning up the tag_type_code
    label = tag_code.replace("tag_generic_", "").replace("_", " ").title()
    return f"🏷️ {label}" if label else "🏷️ Tag"

def load_existing_calendar(path: str) -> tuple[Calendar, set[str]]:
    """
    Load an existing calendar file and return the calendar object and a set of existing UIDs.
    Returns a new empty calendar and empty set if file doesn't exist.
    """
    if not os.path.exists(path):
        print(f"No existing calendar found at {path}. Starting fresh.")
        empty_cal = Calendar()
        empty_cal.add('prodid', '-//ramhee98//oura-tags-ical//EN')
        empty_cal.add('version', '2.0')
        empty_cal.add('x-wr-calname', 'Oura Tags')
        return empty_cal, set()

    try:
        with open(path, 'rb') as f:
            existing_cal = Calendar.from_ical(f.read())

        existing_uids = set()
        for component in existing_cal.walk():
            if component.name == "VEVENT":
                uid = component.get('uid')
                if uid:
                    existing_uids.add(str(uid))

        print(f"Loaded existing calendar with {len(existing_uids)} events.")
        return existing_cal, existing_uids

    except Exception as e:
        print(f"Error loading existing calendar: {e}. Starting fresh.")
        empty_cal = Calendar()
        empty_cal.add('prodid', '-//ramhee98//oura-tags-ical//EN')
        empty_cal.add('version', '2.0')
        empty_cal.add('x-wr-calname', 'Oura Tags')
        return empty_cal, set()

def generate_tags_calendar(tag_data: List[Dict], existing_calendar: Calendar, existing_uids: set[str], custom_tag_names: dict = None) -> Calendar:
    """Generate iCal events from Oura enhanced tag data."""
    cal = existing_calendar

    for tag in tag_data:
        uid = tag.get("id") or str(uuid4())
        if uid in existing_uids:
            print(f"Skipping existing event with UID: {uid}")
            continue

        tag_label = format_tag_label(tag, custom_tag_names)
        tag_code = tag.get("tag_type_code", "unknown")
        comment = tag.get("comment", "")

        # Determine start/end times
        start_time = tag.get("start_time")
        end_time = tag.get("end_time")
        start_day = tag.get("start_day")
        end_day = tag.get("end_day")

        event = Event()
        event.add('uid', uid)
        event.add('dtstamp', datetime.now(timezone.utc))
        event.add('created', datetime.now(timezone.utc))

        if start_time and end_time:
            # Timed event
            try:
                start = datetime.fromisoformat(start_time)
                end = datetime.fromisoformat(end_time)
            except Exception as e:
                print(f"Skipping tag due to invalid time: {e}")
                continue
            event.add('dtstart', start)
            event.add('dtend', end)
        elif start_time:
            # Only start time, create a 0-minute event
            try:
                start = datetime.fromisoformat(start_time)
            except Exception as e:
                print(f"Skipping tag due to invalid time: {e}")
                continue
            event.add('dtstart', start)
            event.add('dtend', start)
        elif start_day:
            # All-day event
            try:
                day = date.fromisoformat(start_day)
            except Exception as e:
                print(f"Skipping tag due to invalid date: {e}")
                continue
            event.add('dtstart', day)
            if end_day and end_day != start_day:
                event.add('dtend', date.fromisoformat(end_day))
        else:
            print(f"Skipping tag with no time information: {uid}")
            continue

        # Build description
        event.add('summary', tag_label)
        if comment:
            event.add('description', comment)

        cal.add_component(event)

    return cal

def save_calendar(calendar: Calendar, path: str):
    with open(path, 'wb') as f:
        f.write(calendar.to_ical())
