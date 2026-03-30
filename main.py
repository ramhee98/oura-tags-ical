from config import OURA_TOKEN, ICAL_OUTPUT_PATH, DAYS_BACK, CUSTOM_TAG_NAMES
from oura_api.client import fetch_tag_data
from ical.generator import generate_tags_calendar, save_calendar, load_existing_calendar

def main():
    print(f"Fetching enhanced tag data for the past {DAYS_BACK} days...")
    tag_data = fetch_tag_data(OURA_TOKEN, days_back=DAYS_BACK)

    if not tag_data:
        print("No tag data found.")
        return

    print("Loading existing calendar...")
    existing_calendar, existing_uids = load_existing_calendar(ICAL_OUTPUT_PATH)

    print(f"Generating calendar with {len(tag_data)} new tag entries...")
    calendar = generate_tags_calendar(
        tag_data,
        existing_calendar,
        existing_uids,
        custom_tag_names=CUSTOM_TAG_NAMES
    )

    print(f"Saving calendar to {ICAL_OUTPUT_PATH}...")
    save_calendar(calendar, ICAL_OUTPUT_PATH)

    print("Done.")

if __name__ == "__main__":
    main()
