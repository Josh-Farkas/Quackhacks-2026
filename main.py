import steamapi
import garminAPI
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.dates as mdates
import numpy as np
from datetime import datetime


def date_to_time(date):
    """Changes datetime date into UNIX timestamp"""
    return int(date.timestamp())


def time_to_date(time):
    """Changes UNIX timestamp to datetime date"""
    return datetime.fromtimestamp(time)


def read_game_data():
    """Returns array of times games were opened, the game's name, and its graph color"""
    game_data = np.genfromtxt(steamapi.GAME_DATA_PATH, delimiter=",", dtype=None, names=True, encoding="utf-8", skip_header=0)
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


def get_stress_values():
    """Returns array of timestamps and corresponding stress values"""
    stress_data = garminAPI.get_stress_values()
    stress_times = stress_data[:, 0] / 1000 # Convert to seconds not ms
    stress_values = stress_data[:, 1]
    stress_values = np.ma.masked_where(stress_values <= 0, stress_values)
    print(stress_times.min(), stress_times.max()) # 1772254800.0 1772303760.0
    return stress_times, stress_values


def get_game_average_stress(stress_times, stress_values, game_times, game_names):
    """Returns the average stress level while playing each game"""
    # Map each stress timestamp to a game name
    labels = np.array([get_game_at(game_times, game_names, t) for t in stress_times])

    return {
        game: np.ma.mean(stress_values[labels == game])
        for game in np.unique(labels)
    }


def plot_game_stress(stress_times, stress_values, game_times, game_names, color_map):
    """Plots stress with colors based on current game."""
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
    stress_times, stress_values = get_stress_values()
    game_times, game_names, color_map = read_game_data()
    # plot_game_stress(stress_times, stress_values, game_times, game_names, color_map)
    # plot_game_average_stress(stress_times, stress_values, game_times, game_names, color_map)


if __name__ == "__main__":
    main()
