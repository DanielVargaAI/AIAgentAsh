from rapidfuzz import process, fuzz


def get_best_match(query, database_dict, score_cutoff=70):
    choices = list(database_dict.keys())

    match, score, idx = process.extractOne(
        query,
        choices,
        scorer=fuzz.WRatio,  # robust gegen OCR-Fehler
        score_cutoff=score_cutoff  # nur Treffer über 70% zulassen
    )

    if match is None:
        return None  # kein Treffer

    return match, database_dict[match]
