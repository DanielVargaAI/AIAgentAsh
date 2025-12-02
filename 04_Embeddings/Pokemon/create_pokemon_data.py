import re
import ast
import json
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import settings


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


def create_pokemon_embeddings():
    with open("pokedex_data.json", "r") as f:
        pkm_data = json.loads(f.read())

    pkm_data_list = []
    pkm_ids = []
    form_counter = 0
    for pkm in pkm_data:
        type1 = pkm["t1"] if "t1" in pkm.keys() else -1
        type2 = pkm["t2"] if "t2" in pkm.keys() else -1
        # use one-hot encoding for types
        combined_type_vector = []
        for i in range(18):
            if i == type1 or i == type2:
                combined_type_vector.append(1)
            else:
                combined_type_vector.append(0)
        ability1 = pkm["a1"] if "a1" in pkm.keys() else -1
        ability2 = pkm["a2"] if "a2" in pkm.keys() else -1
        hidden_ability = pkm["ha"] if "ha" in pkm.keys() else -1
        passive = pkm["pa"] if "pa" in pkm.keys() else -1
        sum_points = pkm["bst"]
        hp = pkm["hp"]
        atk = pkm["atk"]
        defence = pkm["def"]
        spa = pkm["spa"]
        spd = pkm["spd"]
        spe = pkm["spe"]
        generation = pkm["ge"]
        family = pkm["fa"] if "fa" in pkm.keys() else -1
        pkm_vector = combined_type_vector + [ability1, ability2, hidden_ability, passive,
                                             sum_points, hp, atk, defence, spa, spd, spe,
                                             generation, family]
        pkm_data_list.append(pkm_vector)
        if str(pkm["dex"]) != pkm_ids[-1].split("-")[0] if pkm_ids else -1:
            form_counter = 0
            new_key = str(pkm["dex"]) + "-" + str(form_counter)
        else:
            new_key = str(pkm["dex"]) + "-" + str(form_counter)
        form_counter += 1
        pkm_ids.append(new_key)

    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(pkm_data_list)

    pca = PCA(n_components=4)
    move_embeddings = pca.fit_transform(scaled_data)

    move_embedding_dict = {}
    for index, move_id in enumerate(pkm_ids):
        move_embedding_dict[move_id] = move_embeddings[index].tolist()

    with open("pokemon_embeddings.json", "w") as f:
        f.write(json.dumps(move_embedding_dict))


def get_pokemon_embedding(dex: int, form_index: int, embeddings_data: dict = None):
    pkm_key_name = str(dex) + "-" + str(form_index)
    return embeddings_data[pkm_key_name]


def get_similar_pokemon_embeddings(dex: int, form_index: int, top_k: int = 5, embeddings_data: dict = None):
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np

    pkm_key_name = str(dex) + "-" + str(form_index)

    target_embedding = np.array(embeddings_data[pkm_key_name]).reshape(1, -1)
    all_embeddings = []
    all_keys = []
    for key, emb in embeddings_data.items():
        if key != pkm_key_name:
            all_embeddings.append(emb)
            all_keys.append(key)

    all_embeddings = np.array(all_embeddings)
    similarities = cosine_similarity(target_embedding, all_embeddings).flatten()
    top_indices = similarities.argsort()[-top_k:][::-1]

    similar_pokemons = [(all_keys[i], similarities[i]) for i in top_indices]
    return similar_pokemons


if __name__ == "__main__":
    # save_js_to_json()
    # delete_numerical_keys()
    # create_pokemon_embeddings()
    with open("pokemon_embeddings.json", "r") as f:
        embeddings_data = json.loads(f.read())
    # print(get_pokemon_embedding(6, 2))
    print(get_similar_pokemon_embeddings(6, 0, top_k=10, embeddings_data=embeddings_data))
