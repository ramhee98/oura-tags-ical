# Oura Tags iCal

Generate a tag calendar from your Oura Ring [Enhanced Tags](https://support.ouraring.com/hc/en-us/articles/360038676993-How-to-Use-Tags) as an `.ics` file you can import into calendar apps like Google Calendar, Apple Calendar, or Outlook.

## Features

- Fetches enhanced tag data from the Oura API v2
- Converts tags into iCalendar format (`.ics`)
- Preserves existing data: Automatically merges new data with existing calendar entries, preventing data loss
- Duplicate prevention: Skips events that already exist in your calendar based on unique IDs
- Supports pagination for large tag datasets
- Emoji-labeled tags for quick recognition:
  - ☕ Caffeine, 🍷 Alcohol, 🍽️ Late Meal, 😰 Stressful Day
  - 🏋️ Workout, 🌳 Outdoor Time, 🧘 Meditation, 😴 Nap
  - 📱 Screen Time, 🤒 Sick, 🧖 Sauna, 🥶 Cold Exposure
  - 🍺 Beer, 🍷 Wine, ☕ Coffee, ✈️ Airplane
  - 💊 Supplement, 💧 Hydration, 📓 Journal, and more
- Configurable custom tag names with custom icons via `CUSTOM_TAG_NAMES`
- Includes tag comments in event descriptions
- Handles timed events, start-only events, and all-day events
- Compatible with major calendar clients

## Requirements

- Python 3.8+
- Oura API token with `tag` scope
- Dependencies:
  - `icalendar`
  - `requests`

## Setup

1. Clone the repo:
   ```bash
   git clone https://github.com/ramhee98/oura-tags-ical.git
   cd oura-tags-ical
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create `config.py` or copy `config.py.template` and modify it with:
   ```bash
   cp config.py.template config.py
   ```

## Configuration

Edit `config.py` with your settings:

```python
# Your Oura API personal access token (requires 'tag' scope)
OURA_TOKEN = "your-token-here"

# Path where the generated iCalendar (.ics) file will be saved
ICAL_OUTPUT_PATH = "./tags.ics"

# Number of past days to fetch tag data for
DAYS_BACK = 7

# Map custom tag UUIDs to human-readable names (include your own emoji/icon)
# Find your tag UUIDs by running: python3 main.py (check the Description field in generated events)
CUSTOM_TAG_NAMES = {
    "d96e0d94-8f35-4708-a2a6-c575164824cc": "🍵 Matcha Latte",
}
```

## Usage

```bash
python3 main.py
```

This will:
1. Load any existing calendar data from your `tags.ics` file
2. Fetch new enhanced tag data from the Oura API for the specified number of days
3. Merge the new data with existing events (avoiding duplicates)
4. Save the updated calendar to `tags.ics`

**Note**: The script automatically preserves your existing tag data, so you can run it regularly to update your calendar with new entries without losing historical data.

## Example Calendar Output

**Title:**
```
☕ Caffeine
```

**Description:**
```
Tag: tag_generic_caffeine
Day: 2026-03-29
```

**Title (custom tag with configured name):**
```
🍵 Matcha Latte
```

**Description:**
```
Tag: d96e0d94-8f35-4708-a2a6-c575164824cc
Comment: Before bed
Day: 2026-03-29
```

## Related

- [oura-sleep-ical](https://github.com/ramhee98/oura-sleep-ical) — Generate a sleep calendar from Oura Ring data