
with open('user_game_data.csv', 'a+') as f:
    for t in range(1772254800, 1772280000, 180):
        if t - 1772254800 < 60 * 60 * 1:
            game = 'Balatro'
        elif t - 1772254800 < 60 * 60 * 4:
            game = 'None'
        elif t - 1772254800 < 60 * 60 * 5.5:
            game = 'Stardew Valley'
        elif t - 1772254800 < 25200:
            game = 'Minecraft'
        else:
            game = 'None'
        f.write(f'{t},{game}\n')
    f.write(f'{1772280000},{"None"}\n')
    