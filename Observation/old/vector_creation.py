import json


def create_input_vector_from_data(data):
    """
    Create an input vector from the provided data dictionary.

    Args:
        data (dict): A dictionary containing the data to be converted into a vector. Look at decrypted_data.json for an example.
    Returns:
        list: A list representing the input vector.
    """
    vector = []

    pkm_vector_len = 0
    for pokemon in data["party"]:
        pkm_vector = get_pokemon_vector(pokemon)
        vector.extend(pkm_vector)
        pkm_vector_len = len(pkm_vector)

    if len(data["party"]) < 6:
        for _ in range(6 - len(data["party"])):
            vector.extend([0] * pkm_vector_len)

    for enemy_pokemon in data["enemyParty"]:
        pkm_vector = get_pokemon_vector(enemy_pokemon)
        vector.extend(pkm_vector)
        pkm_vector_len = len(pkm_vector)

    if len(data["enemyParty"]) < 2:
        for _ in range(2 - len(data["enemyParty"])):
            vector.extend([0] * pkm_vector_len)

    for modifier_type in ["modifiers", "enemyModifiers"]:
        modifier_vector = get_modifier_vector(data[modifier_type])
        vector.extend(modifier_vector)

    vector.append(data["arena"]["biome"])  # TODO rest of arena data, one-hot encode or embedding of biome
    vector.extend([x / 100 for x in data["pokeballCounts"]])
    vector.append(data["money"]) # TODO scaling?
    vector.append(data["score"])
    vector.append([data["waveIndex"] / 50, data["waveIndex"] / 250])
    # TODO battleType?

    return vector


def get_modifier_vector(modifiers):
    # TODO implement modifier vector creation
    pass


def get_pokemon_vector(pokemon):
    pkm_vector = [int(pokemon["player"])]
    pkm_vector.append(pokemon["species"])  # TODO scale or change to embedded vector
    pkm_vector.append(pokemon["formIndex"])
    pkm_vector.append(pokemon["abilityIndex"])
    pkm_vector.append(int(pokemon["passive"]))
    pkm_vector.append(int(pokemon["shiny"]))
    pkm_vector.append(pokemon["level"])  # TODO find a scaling value
    pkm_vector.append(pokemon["gender"])
    pkm_vector.append(pokemon["hp"])  # TODO find a scaling value (might be stats[0])
    pkm_vector.extend(pokemon["stats"])  # TODO find a scaling value
    pkm_vector.extend([x / 31 for x in pokemon["ivs"]])
    pkm_vector.append(pokemon["nature"])  # TODO one-hot encode or embedding
    # moves
    for move in pokemon["moves"]:
        # TODO get embedding or smth
        continue
    pkm_vector.append(pokemon["status"])  # TODO one-hot encode or embedding
    pkm_vector.append(pokemon["luck"] / 3)  # luck can be 0, 1, 2, 3
    pkm_vector.append(pokemon["teraType"])  # TODO one-hot encode or embedding
    # TODO fusion stuff
    pkm_vector.append(int(pokemon["boss"]))
    # TODO boss segments?
    pkm_vector.extend([x / 6 for x in pokemon["summonData"]["statStages"]])
    # TODO moveQueue? tags?
    pkm_vector.append(int(pokemon["summonData"]["abilitySuppressed"]))
    pkm_vector.extend([x / 6 for x in pokemon["summonData"]["stats"]])
    # TODO types?
    pkm_vector.append(int(pokemon["summonData"]["illusionBroken"]))
    # TODO berriesEatenLast?, moveHistory?
    pkm_vector.append(pokemon["battleData"]["hitCount"])  # TODO scaling?
    pkm_vector.append(int(pokemon["battleData"]["hasBerriesEaten"]))  # TODO berriesEaten?
    # TODO customPokemonData? fusionCustomPokemonData? mysteryEncounterPokemonData? fusion...?
    return pkm_vector
