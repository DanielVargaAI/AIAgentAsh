import Pokemon
import moves
import numpy as np
import json


data = {
    "enemy1_health": float(),
    "enemy1_type1": str(),
    "enemy1_type2": str(),
    "enemy1_level": int(),
    "enemy1_status": str(),
    "enemy2_health": float(),
    "enemy2_type1": str(),
    "enemy2_type2": str(),
    "enemy2_level": int(),
    "enemy2_status": str(),
    "ally1_health": float(),
    "ally1_type1": str(),
    "ally1_type2": str(),
    "ally1_level": int(),
    "ally1_status": str(),
    "ally1_attack1_name": str(),
    "ally1_attack1_pp": float(),
    "ally1_attack2_name": str(),
    "ally1_attack2_pp": float(),
    "ally1_attack3_name": str(),
    "ally1_attack3_pp": float(),
    "ally1_attack4_name": str(),
    "ally1_attack4_pp": float(),
    "ally2_health": float(),
    "ally2_type1": str(),
    "ally2_type2": str(),
    "ally2_level": int(),
    "ally2_status": str(),
    "ally2_attack1_name": str(),
    "ally2_attack1_pp": float(),
    "ally2_attack2_name": str(),
    "ally2_attack2_pp": float(),
    "ally2_attack3_name": str(),
    "ally2_attack3_pp": float(),
    "ally2_attack4_name": str(),
    "ally2_attack4_pp": float(),
}


def create_input_vector(data, move_database, pokemon_database, type_database):
    input_vector = []
    # Enemy 1
    input_vector.extend(Pokemon.get_pokemon_vector(data["enemy1_name"],
                                                  [data["enemy1_type1"], data["enemy1_type2"]],
                                                  data["enemy1_status"],
                                                  data["enemy1_health"],
                                                  data["enemy1_level"], pokemon_database, type_database))
    # Enemy 2
    input_vector.extend(Pokemon.get_pokemon_vector(data["enemy2_name"],
                                                  [data["enemy2_type1"], data["enemy2_type2"]],
                                                  data["enemy2_status"],
                                                  data["enemy2_health"],
                                                  data["enemy2_level"], pokemon_database, type_database))
    # Ally 1
    input_vector.extend(Pokemon.get_pokemon_vector(data["ally1_name"],
                                                  [data["ally1_type1"], data["ally1_type2"]],
                                                  data["ally1_status"],
                                                  data["ally1_health"],
                                                  data["ally1_level"], pokemon_database, type_database))
    # Ally 1 Moves
    for i in range(1, 5):
        move_name = data[f"ally1_attack{i}_name"]
        move_pp = data[f"ally1_attack{i}_pp"]
        move_vector = moves.get_move_vector(move_name, move_pp, move_database)
        input_vector.extend(move_vector)
    # Ally 2
    input_vector.extend(Pokemon.get_pokemon_vector(data["ally2_name"],
                                                  [data["ally2_type1"], data["ally2_type2"]],
                                                  data["ally2_status"],
                                                  data["ally2_health"],
                                                  data["ally2_level"], pokemon_database, type_database))
    # Ally 2 Moves
    for i in range(1, 5):
        move_name = data[f"ally2_attack{i}_name"]
        move_pp = data[f"ally2_attack{i}_pp"]
        move_vector = moves.get_move_vector(move_name, move_pp, move_database)
        input_vector.extend(move_vector)

    return np.array(input_vector).reshape(1, -1)


if __name__ == "__main__":
    with open("move_data.json", "r") as f:
        move_database = json.load(f)
    with open("pokedex_database.json", "r") as f:
        pokemon_data = json.load(f)
    with open("type_embeddings.json", "r") as tf:
        type_embeddings_json = json.loads(tf.read())
