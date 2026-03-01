import steamAPI
import garminAPI
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.dates as mdates
import numpy as np
from datetime import datetime, date, timedelta
import json # dump dict into txt file

_today = date.today().strftime('%Y-%m-%d')

def get_ymd_date(date: date):
    """Returns the date in YYYY/MM/DD format days_ago days from today."""
    return date.strftime('%Y-%m-%d')


def date_to_time(date):
    """Changes datetime date into UNIX timestamp"""
    return int(date.timestamp())


def time_to_date(time):
    """Changes UNIX timestamp to datetime date"""
    return datetime.fromtimestamp(time)

def read_game_data():
    """Returns array of times games were opened, the game's name, and its graph color"""
    game_data = np.genfromtxt(steamAPI.GAME_DATA_PATH, delimiter=",", dtype=None, names=True, encoding="utf-8", skip_header=0)
    game_data = np.array(game_data.tolist())
    game_times = game_data[:, 0].astype(float)
    game_names = game_data[:, 1]
    
    unique_games = list(dict.fromkeys(game_names))
    palette = list(mcolors.TABLEAU_COLORS.values())
    color_map = {game: palette[i % len(palette)] for i, game in enumerate(unique_games)}
    color_map["None"] = "gray"
    return game_times, game_names, color_map


def get_game_at(game_times, game_names, t):
    """Return the game being played at time t."""
    prior = game_times[game_times <= t]
    if len(prior) == 0:
        return "None"
    return game_names[np.argmax(prior)]


def get_stress_values(start_date, end_date):
    """Returns array of timestamps and corresponding stress values"""
    
    stress_data = np.vstack([
        garminAPI.get_stress_values(get_ymd_date(start_date + timedelta(days=d)))
        for d in range((end_date - start_date).days + 1)
    ])
    stress_times = stress_data[:, 0] / 1000 # Convert to seconds not ms
    stress_values = stress_data[:, 1]
    stress_values = np.ma.masked_where(stress_values <= 0, stress_values)
    # print(stress_times.min(), stress_times.max()) # 1772254800.0 1772303760.0
    return stress_times, stress_values


def get_game_average_stress(stress_times, stress_values, game_times, game_names):
    """Returns the average stress level while playing each game"""
    # Map each stress timestamp to a game name
    labels = np.array([get_game_at(game_times, game_names, t) for t in stress_times])

    return {
        game: np.ma.mean(stress_values[labels == game])
        for game in np.unique(labels)
    }


def get_sleep_data(start_date, end_date):
    """Returns the sleep data starting at start date until end date"""
    sleep_data = {
        start_date + timedelta(days=d): garminAPI.get_sleep_data(get_ymd_date(start_date + timedelta(days=d)))
        for d in range((end_date - start_date).days + 1)
    }
    return sleep_data


def get_sleep_scores(start_date, end_date):
    """Returns a list of sleep scores from start_date to end_date"""
    sleep_data = get_sleep_data(start_date, end_date)
    sleep_scores = [sleep_data[d]['dailySleepDTO']['sleepScores']['overall']['value'] for d in sleep_data]
    return sleep_scores



def plot_game_stress(stress_times, stress_values, game_times, game_names, color_map):
    """Plots stress with colors based on current game."""
    # Get latest data
    stress_times, stress_values = get_stress_values()
    game_times, game_names, color_map = read_game_data()

    stress_dates = [time_to_date(t) for t in stress_times]

    fig, ax = plt.subplots(figsize=(12, 4))

    for i in range(len(stress_times) - 1):
        game  = get_game_at(game_times, game_names, stress_times[i])
        color = color_map.get(game, "gray")
        ax.plot(stress_dates[i:i+2], stress_values[i:i+2], color=color, linewidth=2)

    # Legend
    for game, color in color_map.items():
        ax.plot([], [], color=color, label=game, linewidth=2)

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%D %H:%M"))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    fig.autofmt_xdate()  # tilts labels so they don't overlap

    ax.set_xlabel("Time")
    ax.set_ylabel("Stress")
    ax.set_title("Stress Over Time by Game")
    ax.legend()
    plt.tight_layout()
    plt.show()

def get_body_battery_values():
    """Returns array of timestamps and corresponding body battery values"""
    body_battery_data = garminAPI.get_body_battery_values()
    body_battery_times = body_battery_data[:, 0] / 1000
    body_battery_values = body_battery_data[:, 1]
    body_battery_values = np.ma.masked_where(
        body_battery_values < 0, body_battery_values
    )
    # print(body_battery_times.min(), body_battery_times.max())
    return body_battery_times, body_battery_values

def plot_body_battery():
    """Plots body battery values with colors based on current game."""
    # Get latest data
    body_battery_times, body_battery_values = get_body_battery_values()
    game_times, game_names, color_map = read_game_data()

    body_battery_dates = [time_to_date(t) for t in body_battery_times]

    fig, ax = plt.subplots(figsize=(12, 4))

    for i in range(len(body_battery_times) - 1):
        game = get_game_at(game_times, game_names, body_battery_times[i])
        color = color_map.get(game, "gray")
        ax.plot(
            body_battery_dates[i : i + 2],
            body_battery_values[i : i + 2],
            color=color,
            linewidth=2,
        )

    # Legend
    for game, color in color_map.items():
        ax.plot([], [], color=color, label=game, linewidth=2)

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%D %H:%M"))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    fig.autofmt_xdate()  # tilts labels so they don't overlap

    ax.set_xlabel("Time")
    ax.set_ylabel("Body Battery")
    ax.set_title("Body Battery Over Time by Game")
    ax.legend()
    plt.tight_layout()
    plt.show()


def plot_game_average_stress(stress_times, stress_values, game_times, game_names, color_map):
    """Plots the average stress of each game in a bar chart"""
    avg_stress = get_game_average_stress(stress_times, stress_values, game_times, game_names)

    games  = list(avg_stress.keys())
    values = list(avg_stress.values())
    colors = [color_map.get(game, "gray") for game in games]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(games, values, color=colors)
    ax.bar_label(bars, fmt="%.1f", padding=3)

    ax.set_xlabel("Game")
    ax.set_ylabel("Average Stress")
    ax.set_title("Average Stress by Game")
    ax.set_ylim(0, max(values) * 1.15)  # headroom for labels
    plt.xticks(rotation=15, ha="right")
    plt.tight_layout()
    plt.show()


def main():
    # plot_game_stress()

    plot_body_battery()
    # stats = garminAPI.get_stats()

    # # View Stats Dict in a .txt File
    # with open('stats.txt', 'w') as file:
    #     json.dump(stats, file, indent=4)

    # # View Body Battery Values Dict in a .txt File
    # with open('bodyBattery.txt', 'w') as file:
    #     json.dump(get_body_battery_values(), file, indent=4)

    # # View Body Battery Values np array in a .txt File
    # np.savetxt("bodyBatteryValues.txt", garminAPI.get_body_battery_values(), fmt="%i", delimiter=",")

    # print(stats)
    # steamAPI.start_steam_polling()
    # sleep_data = garminAPI.get_sleep_data()
    print(get_sleep_scores(date.today() - timedelta(days=7), date.today()))
    
    stress_times, stress_values = get_stress_values(date.today() - timedelta(days=7), date.today())
    game_times, game_names, color_map = read_game_data()
    # plot_game_stress(stress_times, stress_values, game_times, game_names, color_map)
    # plot_game_average_stress(stress_times, stress_values, game_times, game_names, color_map)


if __name__ == "__main__":
    main()
