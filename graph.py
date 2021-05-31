from osu import AuthHandler, Client
import requests
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

auth = AuthHandler(client_id, client_secret, redirect_uri)
auth.get_auth_token()

client = Client(auth)


def get_user():
    while True:
        user_id = get_valid_int("Enter your user id: ")
        try:
            user = client.get_user(user_id)
            return user
        except requests.exceptions.HTTPError:
            print("That's not a valid id")


def get_user_mode():
    while True:
        mode = input("Type the game mode you play(standard, mania, catch, or taiko): ").lower()
        if mode in valid_modes:
            return mode_to_name[mode]
        print("That's not a valid game mode.")


def round_to_hour(hour, minute, second):
    if second >= 30:
        minute += 1
    if minute >= 30:
        hour += 1
    if hour == 24:
        hour = 0
    return hour


def add_time(hour, tz):
    hour += tz
    if hour < 0:
        hour = 24 + hour
    if hour > 23:
        hour -= 24
    return int(hour)


def organize_data(timestamps):
    time_dict = {f'{time}:00': 0 for time in range(24)}
    timezone = get_valid_int("Enter the utc offset of your timezone (Ex. -6): ")
    for timestamp in timestamps:
        date, time = timestamp.split('T')
        time = time.split('+')[0]
        hour, minute, second = [int(t) for t in time.split(':')]
        hour = round_to_hour(hour, minute, second)
        time_dict[f'{add_time(hour, timezone)}:00'] += 1

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
