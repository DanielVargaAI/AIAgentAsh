from sklearn.decomposition import PCA
from settings import type_matrix
import json


def create_embeddings():
    pca = PCA(n_components=4)
    values = [x for x in type_matrix.values()]
    embeddings = pca.fit_transform(values)
    return embeddings


def create_json(embeddings):
    type_embeddings_dict = dict()
    for index, type_name in enumerate(type_matrix.keys()):
        type_embeddings_dict[type_name] = embeddings[index].tolist()
    print(type_embeddings_dict)
    with open("type_embeddings.json", "w") as f:
        f.write(json.dumps(type_embeddings_dict))


if __name__ == "__main__":
    embeddings = create_embeddings()
    """
    pflanze_vec = embeddings[1]
    distances = np.linalg.norm(embeddings - pflanze_vec, axis=1)
    nearest = np.argsort(distances)[:5]
    print(nearest)
    """
    print(embeddings)
    create_json(embeddings)
