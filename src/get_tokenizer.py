import json
import os.path

import numpy as np
import tqdm

import softmatcha.functional as F
from argparse import ArgumentParser


def download_fasttext_model(name: str) -> str:
    """Download and extract a fasttext model and its vocabulary.

    Args:
        name (str): A model name.

    Returns:
        str: Path to the saved directory.
    """
    import fasttext
    import huggingface_hub

    print(f"downloading {name}")
    path = huggingface_hub.hf_hub_download(f"facebook/{name}", filename="model.bin")
    save_dir = os.path.dirname(os.path.abspath(path))
    save_dir_2 = "/app/src"
    vocab_file = os.path.join(save_dir, "vocab.json")
    embedding_file = os.path.join(save_dir, "embedding.npy")
    print(vocab_file)
    print(embedding_file)
    vocab_file_2 = os.path.join(save_dir_2, "vocab.json")
    embedding_file_2 = os.path.join(save_dir_2, "embedding.json")



    if not os.path.exists(vocab_file) or not os.path.exists(embedding_file):
        print("model loading")
        model = fasttext.load_model(path)
        print("model loaded")
        words = model.get_words(on_unicode_error="replace")
        print("words loaded")
        with open(vocab_file, mode="w") as f:
            json.dump(
                {word: idx for idx, word in enumerate(words)},
                f,
                ensure_ascii=False,
                indent="",
            )
        with open(vocab_file_2, mode="w") as f:
            json.dump(
                {word: idx for idx, word in enumerate(words)},
                f,
                ensure_ascii=False,
                indent="",
            )

        print("malloc embeddings")
        embeddings = np.zeros((len(words) + 1, model.get_dimension()), dtype=np.float32)
        for idx in tqdm.tqdm(range(len(words))):
            embeddings[idx] = F.normalize(model.get_input_vector(idx))
        print("saving embeddings")
        with open(embedding_file, mode="wb") as f:
            np.save(f, embeddings)
        with open(embedding_file_2, mode="wb") as f:
            np.save(f, embeddings)
        print("saved embeddings")

    return save_dir

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--name", type=str)
    args = parser.parse_args()

    download_fasttext_model(args.name)