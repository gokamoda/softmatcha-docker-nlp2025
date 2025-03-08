import re
from argparse import ArgumentParser
from pathlib import Path

import datasets
from tqdm import tqdm


def wikitext103(save_dir: Path):
    save_path = save_dir.joinpath("wikitext-103-raw-v1-train.txt")
    if save_path.exists():
        return
    dataset = datasets.load_dataset(
        "salesforce/wikitext", "wikitext-103-raw-v1", split="train"
    )
    pattern = re.compile(r" @(.)@ ")
    # for subset in ["train"]:
    with open(save_path, "w") as f:
        for line in dataset["text"]:
            f.write(pattern.sub(r"\1", line))


def wikipedia_ja_20230720(save_dir: Path):
    save_path = save_dir.joinpath("wikipedia-ja-20230720-train.txt")
    if save_path.exists():
        return
    dataset = datasets.load_dataset("izumi-lab/wikipedia-ja-20230720", split="train")
    with open(save_path, "w") as f:
        for line in dataset["text"]:
            f.write(line)


def wikipedia_ja_20230720_100k(save_dir: Path):
    save_path = save_dir.joinpath("wikipedia-ja-20230720-100k.txt")
    if save_path.exists():
        return
    dataset = datasets.load_dataset("mmnga/wikipedia-ja-20230720-100k", split="train")
    with open(save_path, "w") as f:
        for line in dataset["text"]:
            f.write(line)


def latin_10m(save_dir: Path):
    # split the dataset into two files as it is too large
    # (to prevent "Python int too large to convert to C long" at indexing)
    save_path_1 = save_dir.joinpath("latin-10m-a.txt")
    save_path_2 = save_dir.joinpath("latin-10m-b.txt")

    # if save_path.exists():
    #     return
    dataset = datasets.load_dataset("itserr/latin_dataset_1.0", split="train")
    with open(save_path_1, "w") as fa, open(save_path_2, "w") as fb:
        for i, line in enumerate(tqdm(dataset["text"])):
            if i < 3000000:
                fa.write(line + "\n")
            else:
                fb.write(line + "\n")


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "--dataset-name",
        type=str,
        choices=[
            "wikitext-103-raw-v1-train",
            "wikipedia-ja-20230720-100k",
            "latin-10m",
        ],
    )
    args = parser.parse_args()

    scripts = {
        "wikitext-103-raw-v1-train": wikitext103,
        "wikipedia-ja-20230720-100k": wikipedia_ja_20230720_100k,
        "latin-10m": latin_10m,
    }
    save_dir = Path("corpora")
    save_dir.mkdir(exist_ok=True)
    scripts[args.dataset_name](save_dir=save_dir)

    # wikitext103(save_dir=save_dir)
    # # wikipedia_ja_20230720()
    # wikipedia_ja_20230720_100k(save_dir=save_dir)
