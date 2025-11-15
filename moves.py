from Pokemon import Pokemon
import settings
import json


def calc_moveset_value(pokemon: Pokemon, moveset):
    moveset_value = 0
    types = set()
    for move in moveset:
        types.add(move.dmg_type)
        corr_pkm_stat = pokemon.stats["Atk"] if move.move_type == "physical" else pokemon.stats["SpA"]  # "basic" missing
        move_value = (corr_pkm_stat * settings.stat_multiplier * move.damage * move.accuracy * move.pp *
                      settings.pp_multiplier * (1 + 0.5 * bool(move.dmg_type in pokemon.dmg_types)))
        moveset_value += move_value
    # TODO maybe reward, if the types are "more" different, e.g. vector-sum from max values against every type
    moveset_value *= settings.multiple_same_type_multiplier * len(types)
    return moveset_value


def calc_best_moveset_combination(pokemon: Pokemon, moveset, new_move):
    """returns the best moveset, given the current moveset, the new move that can be learned and the Pokemon"""
    moveset_values = [0, 0, 0, 0, 0]
    for x in range(4):
        new_moveset = moveset.copy()
        new_moveset[x] = new_move
        moveset_values[x] = calc_moveset_value(pokemon, new_moveset)
    moveset_values[4] = calc_moveset_value(pokemon, moveset)
    return moveset_values.index(max(moveset_values))


def get_vector(self):
    """returns the embedded vector"""
    vector = []
    vector.append(self.dmg_type)  # add embedded vector of the dmg type
    vector.append(self.move_type)  # add vector/id of move type
    vector.append(self.accuracy / 100)  # scaled accuracy [0, 1]
    vector.append(self.pp / 10)  # scaled pp [0.5, ~4]
    vector.append(self.damage / 100)  # scaled dmg [0, ~1.5]
    # TODO append additional info like who get's hit
    return vector


def create_move_json():
    moves_dict = dict()
    with open("move_data.txt", "r") as tf:
        for line in tf.readline():
            splitted = line.split("|")
            name = splitted[2].split("]")[0]
            atk_type = splitted[3].split("_")[1].split(".")[0]
            move_type = splitted[4].split("_")[1].split(".")[0]
            dmg = splitted[5].strip()
            dmg = int(dmg) if dmg != "-" else 0
            acc = splitted[6].strip()
            acc = int(acc) if acc != "-" else 0
            pp = splitted[7].strip()
            pp = int(pp) if pp != "-" else 0
            moves_dict[name] = [atk_type, move_type, dmg, acc, pp]
    with open("move_data.json", "w") as jf:
        jf.write(json.dumps(moves_dict))


if __name__ == "__main__":
    string = "| **[[movedex:1|Absorb]]** | {{gameplay:types:en_Grass.png?nolink&40}} | {{:gameplay:types:move_Special.png?nolink&40}} | 20 | 100 | 25 |"
    splitted = string.split("|")
    print(splitted)
    print(splitted[2].split("]")[0])
    print(splitted[3].split("_")[1].split(".")[0])
    print(splitted[4].split("_")[1].split(".")[0])
    print(splitted[5].strip())
    print(splitted[6].strip())
    print(splitted[7].strip())
