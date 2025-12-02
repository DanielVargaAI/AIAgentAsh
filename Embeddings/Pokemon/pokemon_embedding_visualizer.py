# """
# plot the pokemon embeddings in 2D using PCA and matplotlib
# use the images from r"C:\Users\danie\Desktop\pokerogue_main\assets\images\pokemon" for visualization
# the images are .png files named with the pokemon dex number, e.g. "1.png" for bulbasaur
# go through all pokemon embeddings and plot them in a scatter plot with their images
# use only the first image from the png files for each pokemon (ignore forms for now)
# inside the png files, the pokemon is displayed several times for animation, use the first one
# """
import json
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
import os
from PIL import Image
import matplotlib.offsetbox as offsetbox
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib")
import glob


def load_pokemon_images(image_folder):
    image_dict = {}
    # image files are sorted by generation (folders named "1", "2", ..., "8"), then by dex number (e.g. "1.png", "2.png", ...)
    gen_folders = sorted([f.path for f in os.scandir(image_folder) if f.is_dir() and f.name.isdigit()], key=lambda x: int(os.path.basename(x)))
    for gen_folder in gen_folders:
        # there are files names like "1s.png" for shiny versions, ignore those for now
        image_files = sorted(glob.glob(os.path.join(gen_folder, "[0-9]*.png")), key=lambda x: int(os.path.basename(x).split(".")[0].split("-")[0].split("s")[0]))
        for image_file in image_files:
            dex_number = int(os.path.basename(image_file).split(".")[0].split("-")[0].split("s")[0])
            if dex_number not in image_dict:
                img = Image.open(image_file).convert("RGBA")
                image_dict[dex_number] = img
    return image_dict


def plot_pokemon_embeddings(embeddings_data, image_dict):
    pkm_keys = list(embeddings_data.keys())
    pkm_vectors = [embeddings_data[key] for key in pkm_keys]
    dex_numbers = [int(key.split("-")[0]) for key in pkm_keys]

    pca = PCA(n_components=2)
    reduced_embeddings = pca.fit_transform(pkm_vectors)

    fig, ax = plt.subplots(figsize=(20, 15))
    ax.set_title("Pokemon Embeddings Visualization", fontsize=20)

    # Dummy Punkte für Autoscale
    ax.scatter(reduced_embeddings[:, 0], reduced_embeddings[:, 1], alpha=0)

    for i, dex in enumerate(dex_numbers):
        if dex in image_dict:
            img = image_dict[dex]
            img.thumbnail((40, 40), Image.LANCZOS)  # Resize image to fit better
            imagebox = offsetbox.AnnotationBbox(
                offsetbox.OffsetImage(img, zoom=1),
                (reduced_embeddings[i, 0], reduced_embeddings[i, 1]),
                frameon=False
            )
            ax.add_artist(imagebox)

    ax.set_xlabel("PCA Component 1", fontsize=15)
    ax.set_ylabel("PCA Component 2", fontsize=15)
    plt.grid()
    plt.show()


if __name__ == "__main__":
    with open("pokemon_embeddings.json", "r") as f:
        embeddings_data = json.load(f)

    image_folder = r"C:\Users\danie\Desktop\pokerogue_main\assets\images\pokemon\icons"
    image_dict = load_pokemon_images(image_folder)

    plot_pokemon_embeddings(embeddings_data, image_dict)
