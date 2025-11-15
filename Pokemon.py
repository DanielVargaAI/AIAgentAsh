import json
import re
import ast
import settings
import requests
from sklearn.decomposition import PCA


class Pokemon:
    def __init__(self):
        self.stats = {
            "Atk": 0,
            "SpA": 0,
            "Def": 0,
            "SpD": 0,
            "Spe": 0,
            "HP": 0,
        }
        self.dmg_types = []


def save_js_to_json():
    input_file = "pokedex_data.js"
    output_file = "pokedex_data.json"

    with open(input_file, "r", encoding="utf-8") as f:
        js = f.read()

    # 1. Extrahiere das Array hinter "const items ="
    array_text = re.search(r"const\s+items\s*=\s*(\[.*\]);?", js, re.DOTALL).group(1)

    # 2. JS → Python-Dict-konvertierbar machen
    #    a) Keys mit Anführungszeichen versehen
    array_text = re.sub(r'(\w+):', r'"\1":', array_text)

    # 3. In Python-Daten laden
    py_data = ast.literal_eval(array_text)

    # 4. Als JSON ausgeben
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(py_data, f, ensure_ascii=False, indent=2)

    print("Konvertiert → gespeichert als", output_file)


def delete_numerical_keys():
    pokedex_data_cropped = list()
    with open("pokedex_data.json", "r") as f:
        data = json.loads(f.read())
        for pokemon in data:
            pokedex_data_cropped.append(dict())
            for key in pokemon.keys():
                if not key.isnumeric():
                    pokedex_data_cropped[-1][key] = pokemon[key]
    with open("pokedex_data.json", "w") as f:
        f.write(json.dumps(pokedex_data_cropped))


def create_pokedex_database():
    pokedex_data = dict()
    with open("type_embeddings.json", "r") as tf:
        type_embeddings_json = json.loads(tf.read())
    type_names = list(settings.type_matrix.keys())
    type_names.sort()

    with open("pokedex_data.json", "r") as f:
        data = json.loads(f.read())
        for pokemon in data:
            response = requests.get(str("https://pokeapi.co/api/v2/pokemon/" + str(pokemon["dex"])), data={"species"})
            if response.status_code != 200:
                print(pokemon["img"])
                name = pokemon["img"]
            else:
                name = response.json()["species"]["name"]
            # if the img has "-" add everything behind it in front of the name
            if pokemon["img"].find("-") > 0:
                name = pokemon["img"][pokemon["img"].find("-"):] + "-" + name
            pokedex_data[name] = {"data": [], "embedding": []}
            type1_emb = type_embeddings_json[type_names[pokemon["t1"]]] if "t1" in pokemon.keys() else [0, 0, 0, 0]
            type2_emb = type_embeddings_json[type_names[pokemon["t2"]]] if "t2" in pokemon.keys() else [0, 0, 0, 0]
            ability1 = pokemon["a1"] / 500 if "a1" in pokemon.keys() else -1
            ability2 = pokemon["a2"] / 500 if "a2" in pokemon.keys() else -1
            hidden_ability = pokemon["ha"] / 500 if "ha" in pokemon.keys() else -1
            passive = pokemon["pa"] / 500 if "pa" in pokemon.keys() else -1
            sum_points = pokemon["bst"] / 1125  # E-Max Eternatus with the highest value
            hp = pokemon["hp"] / 255
            atk = pokemon["atk"] / 255
            defence = pokemon["def"] / 255
            spa = pokemon["spa"] / 255
            spd = pokemon["spd"] / 255
            spe = pokemon["spe"] / 255
            generation = pokemon["ge"] / 9  # Generations 1-9
            family = pokemon["fa"] / 1000 if "fa" in pokemon.keys() else -1
            pokedex_data[name]["data"].extend(type1_emb)
            pokedex_data[name]["data"].extend(type2_emb)
            pokedex_data[name]["data"].extend([ability1, ability2, hidden_ability, passive, sum_points, hp, atk, defence, spa, spd, spe, generation, family])

    pokemon_embeddings = create_pokemon_embeddings(pokedex_data)

    for index, pokemon_name in enumerate(pokedex_data.keys()):
        pokedex_data[pokemon_name]["embedding"] = pokemon_embeddings[index].tolist()

    with open("pokedex_database.json", "w") as dbf:
        dbf.write(json.dumps(pokedex_data))


def get_pokemon_vector(name: str, status: str, hp: float, level: int = 0, ):
    """returns the embedded vector"""
    # TODO: Bei fehlerhafter Namensextraktion das passendste finden
    with open("pokedex_database.json", "r") as f:
        move_data = json.load(f)
    vector = move_data[name]["embedding"]
    vector.extend(move_data[name]["data"][0:8])
    vector.extend([status, hp, level])
    return vector


def create_pokemon_embeddings(pokedex_data):
    pca = PCA(n_components=8)
    values = [x["data"] for x in pokedex_data.values()]
    embeddings = pca.fit_transform(values)
    return embeddings


if __name__ == "__main__":
    # save_js_to_json()
    # delete_numerical_keys()
    # create_pokedex_database()
    print(get_pokemon_vector("bulbasaur", "", 0.6, 5))
    # TODO check similarities
