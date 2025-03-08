from argparse import ArgumentParser, Namespace

from softmatcha.cli.build_inverted_index import get_argparser, main


def wikitext103():
    args = Namespace(
        inputs=["corpora/wikitext-103-raw-v1-train.txt"],
        index="corpora/glove-wiki-gigaword-300_wikitext-103-raw-v1-train.h5",
        model="glove-wiki-gigaword-300",
        jsonl_key=None,
        chunk_size=1024,
        backend="gensim",
        num_workers=8,
        buffer_size=10000,
    )
    main(args)
    print("Done")


def wikipedia_ja_20230720():
    args = Namespace(
        inputs="corpora/wikipedia-ja-20230720-train.txt",
        index="corpora/fasttext-ja-vectors_wikipedia-ja-20230720-train.h5",
        model="fasttext-ja-vectors",
        backend="fasttext",
    )
    main(args)
    print("Done")


def wikipedia_ja_20230720_100k():
    args = get_argparser().parse_args()
    print(args)
    main(args)
    args = Namespace(
        inputs=["corpora/wikipedia-ja-20230720-100k.txt"],
        index="corpora/fasttext-ja-vectors_wikipedia-ja-20230720-100k.h5",
        model="fasttext-ja-vectors",
        backend="fasttext",
        jsonl_key=None,
        chunk_size=1024,
        num_workers=2,
        buffer_size=10000,
    )
    main(args)
    print("Done")


def perseus():
    args = Namespace(
        inputs=["corpora/lat_text_perseus_preprocessed.txt"],
        index="corpora/fasttext-la-vectors_perseus.h5",
        model="fasttext-la-vectors",
        backend="fasttext",
        jsonl_key=None,
        chunk_size=1024,
        num_workers=8,
        buffer_size=10000,
    )
    main(args)
    print("Done")


def augstinian_sermon_parallelisms():
    args = Namespace(
        inputs=["corpora/augustinian-sermon-parallelisms.txt"],
        index="corpora/fasttext-la-vectors_augustinian-sermon-parallelisms.h5",
        model="fasttext-la-vectors",
        backend="fasttext",
        jsonl_key=None,
        chunk_size=1024,
        num_workers=8,
        buffer_size=10000,
    )
    main(args)
    print("Done")


def latin_10m():
    args = Namespace(
        inputs=["corpora/latin-10m-a.txt", "corpora/latin-10m-b.txt"],
        index="corpora/fasttext-la-vectors_latin-10m.h5",
        model="fasttext-la-vectors",
        backend="fasttext",
        jsonl_key=None,
        chunk_size=1024,
        num_workers=8,
        buffer_size=10000,
    )
    main(args)
    print("Done")


if __name__ == "__main__":
    # parser = ArgumentParser()
    # parser.add_argument(
    #     "--dataset-name",
    #     type=str,
    #     choices=[
    #         "wikitext-103",
    #         "wikipedia-ja-20230720-100k",
    #         "perseus",
    #         "augstinian-sermon-parallelisms",
    #         "latin-10m",
    #     ],
    # )
    # args = parser.parse_args()

    # scripts = {
    #     "wikitext-103": wikitext103,
    #     "wikipedia-ja-20230720-100k": wikipedia_ja_20230720_100k,
    #     "perseus": perseus,
    #     "augstinian-sermon-parallelisms": augstinian_sermon_parallelisms,
    #     "latin-10m": latin_10m,
    # }
    # scripts[args.dataset_name]()
    args = get_argparser().parse_args()
    main(args)
