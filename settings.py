screen = (1920, 1080)
roi_stage = (1595, 300, 1695, 342)  # TODO is not fixed, depends on enemy items
roi_game = (96, 52, 1823, 1023)
roi_main_menu = (1460, 563, 1778, 978)
image_scaler = (1/3, 1/3)
scaled_game_width = int((roi_game[2] - roi_game[0]) * image_scaler[0])
scaled_game_height = int((roi_game[3] - roi_game[1]) * image_scaler[1])

scaled_screen_width = int(screen[0] * image_scaler[0])
scaled_screen_height = int(screen[1] * image_scaler[1])
action_keymap = {
    0: 'w',  # Up
    1: 'a',  # Left
    2: 's',  # Down
    3: 'd',  # Right
    4: 'Space',  # Confirm / Action
    5: 'Backspace',  # Back / Cancel
    6: 'Enter'  # Start
}

biomes = ["Abyss", "Ancient Ruins", "Badlands", "Beach", "Cave", "Construction Site", "Desert", "Dojo", "Factory", "Fairy Cave", "Forest",
          "Grassy Fields", "Graveyard", "Ice Cave", "Island", "Jungle", "Laboratory", "Lake", "Meadow", "Metropolis", "Mountain", "Plains",
          "Power Plant", "Sea", "Seabed", "Slum", "Snowy Forest", "Space", "Swamp", "Tall Grass", "Temple", "Town", "Volcano", "Wasteland", "End"]
