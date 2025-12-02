# get highest value of "a1", "a2", "ha", "pa" keys in pkm_data
max_ability_index = -1


def get_max_ability_index(pkm_data):
    global max_ability_index
    for pkm in pkm_data:
        for key in ["a1", "a2", "ha", "pa"]:
            if key in pkm.keys() and pkm[key] > max_ability_index:
                max_ability_index = pkm[key]
    return max_ability_index


import json

with open("pokedex_data.json", "r") as f:
    pkm_data = json.loads(f.read())
    print("Max ability index:", get_max_ability_index(pkm_data))
