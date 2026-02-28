import steamapi
import garminAPI
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import csv

game_times = None
game_names = None

stress_times = None
stress_values = None

color_map = {}

def read_game_data():
    game_data = np.genfromtxt(steamapi.GAME_DATA_PATH, delimiter=",", dtype=None, names=True, encoding="utf-8", skip_header=0)
    game_data = np.array(game_data.tolist())
    game_times = game_data[:, 0].astype(float)
    game_names = game_data[:, 1]
    
    unique_games = list(dict.fromkeys(game_names))
    palette = list(mcolors.TABLEAU_COLORS.values())
    color_map = {game: palette[i % len(palette)] for i, game in enumerate(unique_games)}


def get_game_at(t):
    """Return the game being played at time t."""
    prior = game_times[game_times <= t]
    if len(prior) == 0:
        return "Unknown"
    return game_names[np.argmax(prior)]


def get_stress_values():
    stress_data = garminAPI.get_stress_values()
    stress_times = (stress_data[:, 0] - stress_data[0, 0]) / (1000 * 60)
    stress_values = stress_data[:, 1]
    stress_values = np.ma.masked_where(stress_values <= 0, stress_values)



def plot_game_stress():
    """Plots stress with colors based on current game."""
    # Get latest data
    get_stress_values()
    read_game_data()
    
    fig, ax = plt.subplots(figsize=(12, 4))

    for i in range(len(stress_times) - 1):
        game  = get_game_at(stress_times[i])
        color = color_map.get(game, "gray")
        ax.plot(stress_times[i:i+2], stress_values[i:i+2], color=color, linewidth=2)

    #  Legend
    for game, color in color_map.items():
        ax.plot([], [], color=color, label=game, linewidth=2)
    
    plt.plot(stress_times, stress_values)
    plt.show()


def main():
    plot_game_stress()

if __name__ == "__main__":
    main()
