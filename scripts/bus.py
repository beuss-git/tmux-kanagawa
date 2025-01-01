#!/usr/bin/env python3

import requests
import datetime
import pytz

HOGSKOLERINGEN = 42029
API_URL = "https://mpolden.no/atb/v2/departures"
DIRECTION_OUTBOUND = "outbound"
POSSIBLE_LINES = ["25"]

ACTIVE_SCHEDULE = {
    "Monday": [("20:45", "21:00")],
    "Wednesday": [("19:45", "20:00")],
    "Thursday": [("20:45", "21:00")],
}


def make_request(stop_id: int, direction: str):
    response = requests.get(f"{API_URL}/{stop_id}", params={"direction": direction})
    if response.status_code != 200:
        raise Exception("Failed to fetch data from the API.")
    # print(json.dumps(response.json()))
    return response.json()


def is_active_time():
    # return True
    oslo_timezone = pytz.timezone("Europe/Oslo")
    now = datetime.datetime.now(oslo_timezone)
    day_name = now.strftime("%A")  # Get the day name (e.g., "Monday")

    if day_name in ACTIVE_SCHEDULE:
        for start_time_str, end_time_str in ACTIVE_SCHEDULE[day_name]:
            start_time = datetime.datetime.strptime(start_time_str, "%H:%M").time()
            end_time = datetime.datetime.strptime(end_time_str, "%H:%M").time()
            if start_time <= now.time() <= end_time:
                return True
    return False


def find_next_departures(departures, possible_lines, num_departures=2):
    now = datetime.datetime.now()

    filtered_departures = []
    for departure in departures:
        if departure["line"] in possible_lines:
            departure_time = datetime.datetime.fromisoformat(
                departure["scheduledDepartureTime"]
            )

            diff = (departure_time - now).total_seconds() / 60
            if diff > 0:
                filtered_departures.append((departure, diff))

    filtered_departures.sort(key=lambda x: x[1])
    return filtered_departures[:num_departures]


if __name__ == "__main__":
    if is_active_time():
        try:
            data = make_request(HOGSKOLERINGEN, DIRECTION_OUTBOUND)
            next_departures = find_next_departures(data["departures"], POSSIBLE_LINES)
            if next_departures:
                print(f"🚌 {int(next_departures[0][1])}m {int(next_departures[1][1])}m")
            else:
                print("No departures found.")
        except Exception as e:
            print("Fail: ", e)
