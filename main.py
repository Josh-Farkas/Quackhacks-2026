import steamAPI
import garminAPI
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.dates as mdates
from matplotlib.lines import Line2D
import numpy as np
from datetime import datetime, date, timedelta
import report
import os

_today = date.today().strftime('%Y-%m-%d')

def get_ymd_date(date: date):
    """Returns the date in YYYY/MM/DD format."""
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
        garminAPI.get_stress_values(get_ymd_date(start_date + timedelta(d)))
        for d in range((end_date - start_date).days + 1)
    ])
    stress_times = stress_data[:, 0] / 1000 # Convert to seconds not ms
    stress_values = stress_data[:, 1]
    stress_values = np.ma.masked_where(stress_values <= 0, stress_values)
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
    sleep_scores = {d: (sleep_data[d]['dailySleepDTO']['sleepScores']['overall']['value'] if 'sleepScores' in sleep_data[d]['dailySleepDTO'] else None) for d in sleep_data}
    return sleep_scores

def plot_game_stress(stress_times, stress_values, game_times, game_names, color_map):
    """Plots stress with colors based on current game."""
    # Get latest data
    stress_dates = [time_to_date(t) for t in stress_times]

    fig, ax = plt.subplots(figsize=(12, 4))

    # for i in range(len(stress_times) - 1):
    #     game  = get_game_at(game_times, game_names, stress_times[i])
    #     color = color_map.get(game, "gray")
    #     ax.plot(stress_dates[i:i+2], stress_values[i:i+2], color=color, linewidth=2)

    for i in range(len(stress_times) - 1):
        game = get_game_at(game_times, game_names, stress_times[i])

        # Make None grey
        if game == "None":
            color = "gray"
        else:
            color = color_map.get(game, "gray")

        ax.plot(stress_dates[i:i+2], stress_values[i:i+2],
                color=color, linewidth=2)

    # build continuous session blocks for shading
    sessions = []
    current_game = None
    session_start = None

    for i, t in enumerate(stress_times):
        game = get_game_at(game_times, game_names, t)

        if current_game is None:
            current_game = game
            session_start = t
            continue

        if game != current_game:
            # close previous session at the CURRENT timestamp t
            sessions.append({
                "game": current_game,
                "start": session_start,
                "end": t
            })
            # start new session
            current_game = game
            session_start = t

    # close last session to final time
    if current_game is not None and session_start is not None:
        sessions.append({
            "game": current_game,
            "start": session_start,
            "end": stress_times[-1]
        })

    # shading
    for s in sessions:
        if s["game"] == "None":
            continue

        ax.axvspan(
            time_to_date(s["start"]),
            time_to_date(s["end"]),
            color=color_map.get(s["game"], "gray"),
            alpha=0.15,
            zorder=0  # keep shading behind the line
        )

    # Legend
    handles = []

    # Put "None" first if it exists
    if "None" in color_map:
        handles.append(
            Line2D([0], [0],
                color="gray",
                lw=4,
                label="None")
        )

    # Then add all other games
    for game, color in color_map.items():
        if game == "None":
            continue
        handles.append(
            Line2D([0], [0],
                color=color,
                lw=4,
                label=game)
        )

    # for game, color in color_map.items():
    #     ax.plot([], [], color=color, label=game, linewidth=2)

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%D %H:%M"))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    fig.autofmt_xdate()  # tilts labels so they don't overlap

    ax.set_xlabel("Time")
    ax.set_ylabel("Stress")
    ax.set_title("Stress Over Time by Game")
    ax.legend(handles=handles)
    plt.tight_layout()
    return fig
    # plt.show()

def get_body_battery_values(start_date, end_date):
    """Returns array of timestamps and corresponding body battery values"""
    body_battery_data = garminAPI.get_body_battery_data(get_ymd_date(start_date), get_ymd_date(end_date))
    body_battery_times = body_battery_data[:, 0] / 1000
    body_battery_values = body_battery_data[:, 1]
    body_battery_values = np.ma.masked_where(
        body_battery_values == None, body_battery_values
    )
    return body_battery_times, body_battery_values


def plot_body_battery(body_battery_times, body_battery_values, game_times, game_names, color_map):
    """Plots body battery values with colors based on current game."""
    # Get latest data
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
    # plt.show()
    return fig


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
    return fig
    # plt.show()


def get_daily_playtime(game_times, game_names):
    """Returns a dictionary of {date: {game: minutes}}"""
    daily_playtime = {}
    for t, game in zip(game_times, game_names):
        day = time_to_date(t).date()
        if day not in daily_playtime:
            daily_playtime[day] = {}
        if game not in daily_playtime[day]:
            daily_playtime[day][game] = 0
        daily_playtime[day][game] += steamAPI.UPDATE_PERIOD
    return daily_playtime


# def plot_daily_playtime(game_times, game_names):
#     """Plots a stacked bar chart of daily playtime per game."""
#     daily_playtime = get_daily_playtime(game_times, game_names)

#     dates = sorted(daily_playtime.keys())
#     unique_games = list({game for day in daily_playtime.values() for game in day})
#     palette = list(mcolors.TABLEAU_COLORS.values())
#     color_map = {game: palette[i % len(palette)] for i, game in enumerate(unique_games)}

#     fig, ax = plt.subplots(figsize=(12, 5))

#     bottoms = np.zeros(len(dates))
#     for game in unique_games:
#         values = [daily_playtime[day].get(game, 0) for day in dates]
#         ax.bar(dates, values, bottom=bottoms, label=game, color=color_map[game])
#         bottoms += np.array(values)

#     ax.set_xlabel("Date")
#     ax.set_ylabel("Playtime (minutes)")
#     ax.set_title("Daily Playtime by Game")
#     ax.legend()
#     plt.xticks(rotation=45, ha="right")
#     plt.tight_layout()
#     # plt.show()
#     return fig

def get_sleep_correlation(game_times, game_names, sleep_scores):
    """Calculates how a game effects your sleep"""
    daily_playtime = get_daily_playtime(game_times, game_names)
    game_weighted_sleep = {}
    game_total_playtime = {}

    for day, games in daily_playtime.items():
        sleep_score = sleep_scores.get(day)
        if sleep_score is None:
            continue
        for game, playtime in games.items():
            print(game, playtime)
            if game not in game_weighted_sleep:
                game_weighted_sleep[game] = 0
                game_total_playtime[game] = 0
            game_weighted_sleep[game] += sleep_score * playtime
            game_total_playtime[game] += playtime

    return {
        game: game_weighted_sleep[game] / game_total_playtime[game]
        for game in game_total_playtime
    }


def setup():
    import os

ENV_FILE = ".env"

def save_to_env(key, value):
    """Write or update a key in the .env file."""
    lines = []
    found = False

    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, "r") as f:
            lines = f.readlines()
        for i, line in enumerate(lines):
            if line.startswith(f"{key}="):
                lines[i] = f"{key}={value}\n"
                found = True
                break

    if not found:
        lines.append(f"{key}={value}\n")

    with open(ENV_FILE, "w") as f:
        f.writelines(lines)


def setup():
    print("=== Setup ===\n")

    steam_api_key = input("Steam API key: ").strip()
    save_to_env("STEAM_API_KEY", steam_api_key)
    
    steam_id = input("Steam user ID: ").strip()
    save_to_env("STEAM_ID", steam_id)

    print()
    garmin_user = input("Garmin email: ").strip()
    save_to_env("GARMIN_EMAIL", garmin_user)

    garmin_pass = input("Garmin password: ").strip()
    save_to_env("GARMIN_PASSWORD", garmin_pass)

    print("\nSaved user info.")
    steamAPI.update_env()


def generate_report():
    sleep_data = garminAPI.get_sleep_data()
    sleep_scores = get_sleep_scores(date.today() - timedelta(days=8), date.today() - timedelta(days=1))
    
    stress_times, stress_values = get_stress_values(date.today() - timedelta(1), date.today() - timedelta(1))
    game_times, game_names, color_map = read_game_data()
    body_battery_times, body_battery_values = get_body_battery_values(date.today() - timedelta(1), date.today() - timedelta(1))

    stress_over_time = plot_game_stress(stress_times, stress_values, game_times, game_names, color_map)
    avg_stress_per_game = plot_game_average_stress(stress_times, stress_values, game_times, game_names, color_map)
    body_battery_over_time = plot_body_battery(body_battery_times, body_battery_values, game_times, game_names, color_map)
    # daily_playtime = plot_daily_playtime(game_times, game_names)
    # sleep_correlation = get_sleep_correlation(game_times, game_names, sleep_scores)
    
    # print(sleep_correlation)
    # print(get_daily_playtime(game_times, game_names))

    report.generate_report(
        stress_over_time, avg_stress_per_game, body_battery_over_time)



def main():
    while True:
        ui = input("Type 1, 2, 3, q to exit:\n(1) Set Steam ID, API Key and Garmin Login\n(2) Generate Report \n(3) Run Steam Monitoring\n> ")
        while ui not in ['1', '2', '3', 'q', 'Q']:
            print("Invalid input.")
            ui = input("Type 1, 2, 3, q to exit:\n(1) Set Steam ID, API Key and Garmin Login\n(2) Generate Report \n(3) Run Steam Monitoring\n> ")
        
        if ui == "1":
            setup()
        elif ui == "2":
            generate_report()
        elif ui == "3":
            steamAPI.start_steam_polling()
            while input("Type q to quit.") != "q": pass
            exit()
        elif ui == "q" or ui == "Q":
            exit()
        else:
            continue


if __name__ == "__main__":
    main()
