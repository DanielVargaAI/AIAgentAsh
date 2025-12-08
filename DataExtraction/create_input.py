import Embeddings.Pokemon.create_pokemon_data as pkm_data
import Embeddings.moves.compute_move_data as move_data
import json


def create_input_vector(dict, pokemon_embeddings_data: dict, move_embeddings_data: dict) -> tuple:
    input_vector = []
    meta_data = {"phaseName": dict["phase"]["phaseName"], "stage": dict["metaData"]["waveIndex"],
                 "hp_values": {"enemies": {}, "players": {}}, "is_double_fight": dict["metaData"]["isDoubleFight"],
                 "shop_items": dict["shopItems"]}
    for pkm in dict["enemy"]:
        pkm_embedding = pkm_data.get_pokemon_embedding(pkm["dex_nr"], pkm["formIndex"], pokemon_embeddings_data)
        current_hp = pkm["hp"] / pkm["stats"][0]
        meta_data["hp_values"]["enemies"][pkm["id"]] = pkm["hp"] / pkm["stats"][0]
        input_vector.extend(pkm_embedding + [current_hp])
    if len(dict["enemy"]) < 2:
        for _ in range(2 - len(dict["enemy"])):
            input_vector.extend([0.0] * 9)
    for pkm in dict["player"][:2]:
        pkm_embedding = pkm_data.get_pokemon_embedding(pkm["dex_nr"], pkm["formIndex"], pokemon_embeddings_data)
        current_hp = pkm["hp"] / pkm["stats"][0]
        meta_data["hp_values"]["players"][pkm["id"]] = pkm["hp"] / pkm["stats"][0]
        is_visible = 1.0 if pkm["visible"] else 0.0
        stats = [value / sum(pkm["stats"]) for value in pkm["stats"]]
        moveset = []
        for move_id in range(4):
            if move_id + 1 < len(pkm["moveset"]):
                moveset.extend(move_data.get_move_embedding(pkm["moveset"][move_id]["id"], move_embeddings_data))
            else:
                moveset.extend([0.0] * 4)
        input_vector.extend(pkm_embedding + [current_hp] + stats + moveset + [is_visible])
    if len(dict["player"]) < 2:
        for _ in range(2 - len(dict["player"])):
            input_vector.extend([0.0] * 32)
    return input_vector, meta_data


if __name__ == "__main__":
    with open("../Embeddings\\Pokemon\\pokemon_embeddings.json", "r") as f:
        pokemon_embeddings_data = json.loads(f.read())
    with open(r"../Embeddings/moves/move_embeddings.json", "r") as f:
        move_embeddings_data = json.loads(f.read())
    data_dummy = {'enemy': [{'dex_nr': 263, 'formIndex': 0, 'hp': 14, 'stats': [14, 5, 6, 6, 6, 8]}], 'player': [{'dex_nr': 702, 'formIndex': 0, 'hp': 22, 'moveset': [{'id': 39}, {'id': 609}, {'id': 33}, {'id': 586}], 'stats': [22, 12, 11, 14, 13, 16], 'visible': True}, {'dex_nr': 704, 'formIndex': 0, 'hp': 20, 'moveset': [{'id': 33}, {'id': 71}, {'id': 55}, {'id': 692}], 'stats': [20, 11, 10, 10, 14, 10], 'visible': False}, {'dex_nr': 434, 'formIndex': 0, 'hp': 22, 'moveset': [{'id': 10}, {'id': 139}, {'id': 364}, {'id': 845}], 'stats': [22, 12, 13, 9, 10, 13], 'visible': False}, {'dex_nr': 921, 'formIndex': 0, 'hp': 20, 'moveset': [{'id': 10}, {'id': 45}, {'id': 84}, {'id': 409}], 'stats': [20, 13, 7, 10, 8, 12], 'visible': False}, {'dex_nr': 211, 'formIndex': 0, 'hp': 23, 'moveset': [{'id': 33}, {'id': 40}, {'id': 106}, {'id': 839}], 'stats': [23, 17, 12, 12, 12, 14], 'visible': False}, {'dex_nr': 165, 'formIndex': 0, 'hp': 20, 'moveset': [{'id': 33}, {'id': 48}, {'id': 676}, {'id': 575}], 'stats': [20, 9, 8, 10, 14, 11], 'visible': False}]}
    input_vector = create_input_vector(data_dummy, pokemon_embeddings_data, move_embeddings_data)
    print(input_vector)
    print(len(input_vector))
