import json
from argparse import Namespace

from softmatcha.embeddings import get_embedding
from softmatcha.struct import IndexInvertedFileCollection
from softmatcha.tokenizers import get_tokenizer

from search import get_formatted_search_result


def test():
    # backend = "gensim"
    # model = "glove-wiki-gigaword-300"
    # filename = "glove-wiki-gigaword-300_wikitext-103-raw-v1-train"

    backend = "fasttext"
    model = "fasttext-ja-vectors"
    filename = "fasttext-ja-vectors_wikipedia-ja-20230720-100k"

    embedding_class = get_embedding(backend)
    embedding = embedding_class.build(embedding_class.Config(model))

    tokenizer_class = get_tokenizer(backend)
    tokenizer = tokenizer_class.build(tokenizer_class.Config(model))

    args_dict = {
        "threshold": 0.5,
        "pattern": "march 1 , 2016",
        "start_line": 0,
        "max_lines": 250,
    }

    results = get_formatted_search_result(
        **args_dict,
        embedding=embedding,
        tokenizer=tokenizer,
        indexes=IndexInvertedFileCollection.load("corpora/" + filename + ".h5"),
    )
    print(json.dumps(results))

def test_index_inverted_file_collection():
    filename = "fasttext-ja-vectors_nlp2025"
    indexes = IndexInvertedFileCollection.load("data/" + filename + ".h5")

    from IPython import embed

    embed()


if __name__ == "__main__":
    # test()
    test_index_inverted_file_collection()
