from osu import Client
from requests.exceptions import HTTPError
from pytz import all_timezones, timezone
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt


valid_modes = ['catch', 'mania', 'standard', 'taiko']
mode_to_name = {'catch': 'fruits', 'mania': 'mania',
                'standard': 'osu', 'taiko': 'taiko'}


def get_valid_int(msg):
    while True:
        num = input(msg)
        try:
            num = int(num)
            return num
        except ValueError:
            print("That's not a valid number")


client_id = get_valid_int("Enter your client id: ")
client_secret = input("Enter your client secret: ").strip()
redirect_uri = input("Enter your redirect uri: ").strip()

client = Client.from_client_credentials(client_id, client_secret, redirect_uri)


# Some timezone info
tz_abbreviations = {}
for name in all_timezones:
    tzone = timezone(name)
    for _, _, abbr in getattr(tzone, "_transition_info", [[None, None, datetime.now(tzone).tzname()]]):
        if abbr not in tz_abbreviations:
            tz_abbreviations[abbr] = []
        if name in tz_abbreviations[abbr]:
            continue
        tz_abbreviations[abbr].append(name)


def get_user():
    while True:
        user_id = get_valid_int("Enter your user id: ")
        try:
            user = client.get_user(user_id)
            return user
        except HTTPError:
            print("That's not a valid id")


def get_user_mode():
    while True:
        mode = input("Type the game mode you play(standard, mania, catch, or taiko): ").lower()
        if mode in valid_modes:
            return mode_to_name[mode]
        print("That's not a valid game mode.")


def get_timezone():
    tz = None
    lower_timezones = list(map(str.lower, all_timezones))
    while tz is None:
        tz = input("Enter your timezone (Ex. America/Louisville): ")
        if tz not in lower_timezones:
            if tz.upper() in tz_abbreviations:
                tz = tz_abbreviations[tz.upper()][0]
            else:
                tz = None
                print("Invalid timezone. Try checking out this site if you're having troubles "
                      "entering a correct timezone: https://www.ibm.com/docs/en/cloudpakw3700/"
                      "2.3.0.0?topic=SS6PD2_2.3.0/doc/psapsys_restapi/time_zone_list.html")
        else:
            tz = all_timezones[lower_timezones.index(tz)]
    return timezone(tz)


def organize_data(timestamps):
    tz = get_timezone()
    formatted_ts = [ts.astimezone(tz) for ts in timestamps]
    time_dict = {f"{hour:02}:00": 0 for hour in range(24)}
    for ts in formatted_ts:
        ts = ts.replace(second=0, microsecond=0, minute=0, hour=ts.hour)+timedelta(hours=ts.minute//30)
        time_dict[ts.strftime("%H:00")] += 1

    return time_dict


def main():
    user = get_user()
    game_mode = get_user_mode()
    timestamps = [
        score.created_at for score in
        client.get_user_scores(user.id, 'best', limit=user.scores_best_count, mode=game_mode)
    ]
    data = organize_data(timestamps)
    hours = list(data.values())
    nums = list(data.keys())
    fig, ax = plt.subplots()
    ax.barh(nums, hours)
    ax.set_xticks(np.arange(0, max(list(data.values())), 5))
    ax.set_yticks(np.arange(0, 24, 1))
    fig.savefig('top_play_hours.png', transparent=False)
    print("The graph has been saved as top_play_hours.png")


main()
