import hashlib
from sklearn.decomposition import PCA
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


def get_vector(name: str, pp: float):
    """returns the embedded vector"""
    # TODO: Bei fehlerhafter Namensextraktion das passendste finden
    with open("move_data.json", "r") as f:
        move_data = json.load(f)
    vector = move_data[name]["embedding"]
    vector.extend(move_data[name]["data"][1:8])
    vector.append(pp)
    return vector


def create_move_json():
    moves_dict = dict()
    cheap_hash = lambda input: hashlib.md5(input.encode("utf-8")).hexdigest()[:6]
    type_embeddings = json.loads(open("type_embeddings.json").read())
    with open("move_data.txt", "r") as tf:
        for line in tf:
            splitted = line.split("|")
            name = splitted[2].split("]")[0]
            name_hash = int(cheap_hash(name), 16) / 1_000_000  # numeric form of the hash
            atk_type = splitted[3].split("_")[1].split(".")[0]
            atk_type_emb = type_embeddings[atk_type]
            move_type = splitted[4].split("_")[1].split(".")[0]
            move_type_enc = -1 if move_type == "Status" else 0 if move_type == "Physical" else 1  # only 3 different values possible
            dmg = splitted[5].strip()
            dmg = int(dmg) if dmg != "-" else -1  # Status and some other moves have "-" for no initial damage
            dmg /= 100  # [0 or -1; 2.5]  => 0 Damage - maximum of 250 damage, Status moves with no damage have value -1
            acc = splitted[6].strip()
            acc = int(acc) if acc != "-" else 150  # there are some moves who have "-" for "definitely hitting"
            acc /= 100  # [0; 1.5]  => 0% Accuracy - 100% or dummy value 150% for always hit
            pp = splitted[7].strip()
            pp = int(pp) if pp != "-" else 0  # there should be no move with less than 5 PP
            pp /= 10  # [0.5; 8]
            moves_dict[name] = {"data": [], "embedding": []}
            moves_dict[name]["data"] = [name_hash]
            moves_dict[name]["data"].extend(atk_type_emb)
            moves_dict[name]["data"].extend([move_type_enc, dmg, acc, pp])

    move_embeddings = create_move_embeddings(moves_dict)

    for index, move_name in enumerate(moves_dict.keys()):
        moves_dict[move_name]["embedding"] = move_embeddings[index].tolist()

    with open("move_data.json", "w") as jf:
        jf.write(json.dumps(moves_dict))


def create_move_embeddings(moves_dict):
    pca = PCA(n_components=5)
    values = [x["data"] for x in moves_dict.values()]
    embeddings = pca.fit_transform(values)
    return embeddings


if __name__ == "__main__":
    create_move_json()
    print(get_vector("Absorb", 0.5))
