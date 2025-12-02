import requests
import json
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import os


def collect_move_data():
    """Collects move data from the PokeAPI and stores it in a dictionary."""
    moves_dict = {}

    for move_id in range(938):
        url = "https://pokeapi.co/api/v2/move/" + str(move_id + 1)
        response = requests.get(url)
        if response.status_code != 200:
            continue
        move_data = response.json()
        if move_data["meta"] is None:
            continue
        moves_dict[move_id + 1] = {"accuracy": int(move_data.get("accuracy")) if move_data.get("accuracy") is not None else 0,
                                   "damage_class": int(move_data["damage_class"]["url"].split("/")[-2]),
                                   "power": int(move_data["power"]) if move_data["power"] is not None else 0,
                                   "pp": int(move_data["pp"]) if move_data["pp"] is not None else 0,
                                   "ailment": int(move_data["meta"]["ailment"]["url"].split("/")[-2]),
                                   "ailment_chance": int(move_data["meta"]["ailment_chance"]) if move_data["meta"][
                                                                                                     "ailment_chance"] is not None else 0,
                                   "category": int(move_data["meta"]["category"]["url"].split("/")[-2]),
                                   "crit_rate": int(move_data["meta"]["crit_rate"]) if move_data["meta"]["crit_rate"] is not None else 0,
                                   "drain": int(move_data["meta"]["drain"]) if move_data["meta"]["drain"] is not None else 0,
                                   "flinch_chance": int(move_data["meta"]["flinch_chance"]) if move_data["meta"]["flinch_chance"] is not None else 0,
                                   "healing": int(move_data["meta"]["healing"]) if move_data["meta"]["healing"] is not None else 0,
                                   "min_hits": int(move_data["meta"]["min_hits"]) if move_data["meta"]["min_hits"] is not None else 0,
                                   "max_hits": int(move_data["meta"]["max_hits"]) if move_data["meta"]["max_hits"] is not None else 0,
                                   "min_turns": int(move_data["meta"]["min_turns"]) if move_data["meta"]["min_turns"] is not None else 0,
                                   "max_turns": int(move_data["meta"]["max_turns"]) if move_data["meta"]["max_turns"] is not None else 0,
                                   "stat_chance": int(move_data["meta"]["stat_chance"]) if move_data["meta"]["stat_chance"] is not None else 0,
                                   "priority": int(move_data["priority"]) if move_data["priority"] is not None else 0,
                                   "target": int(move_data["target"]["url"].split("/")[-2]),
                                   "type": int(move_data["type"]["url"].split("/")[-2])}

    with open("collected_move_data.json", "w") as f:
        f.write(json.dumps(moves_dict))


def create_move_embeddings():
    """Creates move embeddings from the collected move data."""
    with open("collected_move_data.json", "r") as f:
        moves_dict = json.loads(f.read())

    move_data_list = []
    move_names = []
    for move_id, data in moves_dict.items():
        move_vector = [data["accuracy"], data["damage_class"], data["power"], data["pp"],
                       data["ailment"], data["ailment_chance"], data["category"], data["crit_rate"],
                       data["drain"], data["flinch_chance"], data["healing"], data["min_hits"],
                       data["max_hits"], data["min_turns"], data["max_turns"], data["stat_chance"],
                       data["priority"], data["target"], data["type"]]
        move_data_list.append(move_vector)
        move_names.append(move_id)

    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(move_data_list)

    pca = PCA(n_components=4)
    move_embeddings = pca.fit_transform(scaled_data)

    move_embedding_dict = {}
    for index, move_id in enumerate(move_names):
        move_embedding_dict[move_id] = move_embeddings[index].tolist()

    with open("move_embeddings.json", "w") as f:
        f.write(json.dumps(move_embedding_dict))


def get_move_embedding(move_id: int, embeddings_data: dict) -> list:
    """Returns the embedding for a given move ID."""
    if move_id not in embeddings_data.keys():
        return embeddings_data.get(str(move_id), [0] * 4)  # return zero vector if move_id not found
    else:
        return embeddings_data[move_id]


if __name__ == "__main__":
    # collect_move_data()
    # create_move_embeddings()
    with open("move_embeddings.json", "r") as f:
        move_embeddings = json.loads(f.read())
        print(get_move_embedding(39, move_embeddings))  # Example usage
