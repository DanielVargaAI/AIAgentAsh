import Embeddings.Pokemon.create_pokemon_data as pkm_data
import Embeddings.moves.compute_move_data as move_data
import json


def create_input_vector(dict, pokemon_embeddings_data: dict, move_embeddings_data: dict) -> tuple:
    input_vector = []
    
    meta_data = {"phaseName": dict["phase"]["phaseName"], "stage": dict["metaData"]["waveIndex"],
                 "hp_values": {"enemies": {}, "players": {}}, "is_double_fight": dict["metaData"]["isDoubleFight"],
                 "shop_items": dict["shopItems"], "learning_pokemon": None, "current_moves_count": 4}
    
    # If in LearnMovePhase, identify which Pokemon is learning
    if meta_data["phaseName"] == "LearnMovePhase":
        player_pokemon = dict.get("player", [])
        if player_pokemon and len(player_pokemon) > 0:
            # The first Pokemon in the party is usually the one learning
            learning_poke = player_pokemon[0]
            meta_data["learning_pokemon"] = {
                "dex_nr": learning_poke.get("dex_nr"),
                "id": learning_poke.get("id"),
                "name": f"Pokemon_{learning_poke.get('dex_nr')}"
            }
            # Count current moves (movesets with valid move IDs)
            moveset = learning_poke.get("moveset", [])
            move_count = sum(1 for move in moveset if move and move.get("id"))
            meta_data["current_moves_count"] = move_count
    
    for pkm in dict["enemy"]:
        pkm_embedding = pkm_data.get_pokemon_embedding(pkm["dex_nr"], pkm["formIndex"], pokemon_embeddings_data)
        current_hp = pkm["hp"] / pkm["stats"][0]
        meta_data["hp_values"]["enemies"][pkm["id"]] = pkm["hp"] / pkm["stats"][0]
        input_vector.extend(pkm_embedding + [current_hp])
    
    if len(dict.get("enemy", [])) < 2:
        for _ in range(2 - len(dict.get("enemy", []))):
            input_vector.extend([0.0] * 9)

    # --- FIX: Populate HP for ALL party members first ---
    # This ensures SwitchPhase logic sees reserves, even if they aren't in the embedding vector.
    for pkm in dict.get("player", []):
        current_hp = pkm.get("hp", 1) / max(pkm.get("stats", [1])[0], 1)
        meta_data["hp_values"]["players"][pkm.get("id")] = current_hp
    # --------------------------------------------------
    
    # Create Embeddings only for the active Pokemon (First 2)
    for pkm in dict.get("player", [])[:2]:
        pkm_embedding = pkm_data.get_pokemon_embedding(pkm.get("dex_nr"), pkm.get("formIndex"), pokemon_embeddings_data)
        current_hp = pkm.get("hp", 1) / max(pkm.get("stats", [1])[0], 1)
        
        # Note: meta_data["hp_values"] is now already populated for all players above.
        
        is_visible = 1.0 if pkm.get("visible") else 0.0
        stats = [value / max(sum(pkm.get("stats", [1])), 1) for value in pkm.get("stats", [0] * 6)]
        moveset = []
        for move_id in range(4):
            if move_id < len(pkm.get("moveset", [])) and pkm["moveset"][move_id]:
                moveset.extend(move_data.get_move_embedding(pkm["moveset"][move_id].get("id"), move_embeddings_data))
            else:
                moveset.extend([0.0] * 4)
        input_vector.extend(pkm_embedding + [current_hp] + stats + moveset + [is_visible])
    
    if len(dict.get("player", [])) < 2:
        for _ in range(2 - len(dict.get("player", []))):
            input_vector.extend([0.0] * 32)
    
    return input_vector, meta_data


if __name__ == "__main__":
    with open("../Embeddings\\Pokemon\\pokemon_embeddings.json", "r") as f:
        pokemon_embeddings_data = json.loads(f.read())
    with open(r"../Embeddings/moves/move_embeddings.json", "r") as f:
        move_embeddings_data = json.loads(f.read())
    data_dummy = {'enemy': [{'dex_nr': 263, 'formIndex': 0, 'hp': 14, 'stats': [14, 5, 6, 6, 6, 8]}], 'player': [{'dex_nr': 702, 'formIndex': 0, 'hp': 22, 'moveset': [{'id': 39}, {'id': 609}, {'id': 33}, {'id': 586}], 'stats': [22, 12, 11, 14, 13, 16], 'visible': True}, {'dex_nr': 704, 'formIndex': 0, 'hp': 20, 'moveset': [{'id': 33}, {'id': 71}, {'id': 55}, {'id': 692}], 'stats': [20, 11, 10, 10, 14, 10], 'visible': False}, {'dex_nr': 434, 'formIndex': 0, 'hp': 22, 'moveset': [{'id': 10}, {'id': 139}, {'id': 364}, {'id': 845}], 'stats': [22, 12, 13, 9, 10, 13], 'visible': False}, {'dex_nr': 921, 'formIndex': 0, 'hp': 20, 'moveset': [{'id': 10}, {'id': 45}, {'id': 84}, {'id': 409}], 'stats': [20, 13, 7, 10, 8, 12], 'visible': False}, {'dex_nr': 211, 'formIndex': 0, 'hp': 23, 'moveset': [{'id': 33}, {'id': 40}, {'id': 106}, {'id': 839}], 'stats': [23, 17, 12, 12, 12, 14], 'visible': False}, {'dex_nr': 165, 'formIndex': 0, 'hp': 20, 'moveset': [{'id': 33}, {'id': 48}, {'id': 676}, {'id': 575}], 'stats': [20, 9, 8, 10, 14, 11], 'visible': False}]}
    input_vector, meta_data = create_input_vector(data_dummy, pokemon_embeddings_data, move_embeddings_data)
    print(f"Vector Length: {len(input_vector)}")
    print(f"Meta Data Player HP Keys (Should be 6): {len(meta_data['hp_values']['players'].keys())}")