from argparse import Namespace
from collections import defaultdict
from pprint import pformat
import json
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from softmatcha.embeddings import get_embedding
from softmatcha.struct import IndexInvertedFileCollection
from softmatcha.tokenizers import get_tokenizer


class SoftMatchaAPI(FastAPI):
    templates: Jinja2Templates
    embedding_model_infos: dict[str, str] = {
        "glove-wiki-gigaword-300": "gensim",
        "fasttext-ja-vectors": "fasttext",
    }

    index_filenames: dict[str, dict[str, str]] = {
        "en": {
            "NLP2025_en": "glove-wiki-gigaword-300_nlp2025",
        },
        "ja": {
            "NLP2025_ja": "fasttext-ja-vectors_nlp2025",
        },
    }


    # TODO(kamoda): These class variables are no longer needed.
    # corpus_model_combinations: dict[str, list[str]] = {}
    # corpus_model_options: list[str] = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add the templates directory
        self.templates = Jinja2Templates(directory="templates")
        # Add the static directory
        self.mount("/static", StaticFiles(directory="static"), name="static")
        self.corpus_model_options = self.get_corpus_model_options()
        self.corpus_model_combinations = self.get_corpus_model_combinations()
        self.corpus_options = self.get_corpus_options()

    def get_corpus_model_options(self) -> list[str]:
        corpus_model_options = []
        for lang, corpus_dict in self.index_filenames.items():
            corpus_model_options += [f"{lang}--------"] + [
                corpus + " | " + filename.split("_")[0]
                for corpus, filename in corpus_dict.items()
            ]
        return corpus_model_options

    def get_corpus_model_combinations(self) -> dict[str, list[str]]:
        corpus_model_combinations: dict[str, list[str]] = defaultdict(list)
        for _lang, filenames in self.index_filenames.items():
            for key, filename in filenames.items():
                model_name = filename.split("_")[0]
                corpus_model_combinations[key].append(model_name)
        return corpus_model_combinations

    def get_corpus_options(self) -> list[str]:
        corpus_options: list[str] = []
        for _lang, filenames in self.index_filenames.items():
            for key, _filename in filenames.items():
                corpus_options.append(key)
        return corpus_options

    def load_indexes(self) -> dict[str, IndexInvertedFileCollection]:
        """Loads the indexes.

        Returns:
            dict[str, IndexInvertedFileCollection]: Loaded indexes.
        """
        indexes: dict[str, IndexInvertedFileCollection] = {}

        # TODO: This variable is not used.
        # memory_usage: dict[str, float] = {"total": 0.0}

        for _lang, filenames in self.index_filenames.items():
            for key, filename in filenames.items():
                indexes[key] = IndexInvertedFileCollection.load(
                    "data/" + filename + ".h5"
                )
                # memory_usage[key] = sys.getsizeof(indexes[key]) / 1024**3
                # memory_usage["total"] += memory_usage[key]

        return indexes

    def load_line_infos(self) -> dict[str, dict[int, str]]:
        line_infos = {}
        for _lang, filenames in self.index_filenames.items():
            for key, filename in filenames.items():
                line_info_file_path = "data/txt/" + key + ".json"

                with open(line_info_file_path) as fi:
                    line_info_dict = json.load(fi)
                
                line_infos[key] = line_info_dict
        
        return line_infos
                    


def get_model_tokenizers(embedding_model_infos):
    tokenizers = {}
    embedding_models = {}
    model_options = []

    memory_usage = {"total": 0}
    for model, backend in embedding_model_infos.items():
        print(f"Loading gensim model {model}")

        embedding_class = get_embedding(backend)
        embedding_models[model] = embedding_class.build(
            embedding_class.Config(model, mmap=False)
        )

        # might have overlapping tokenizers.
        tokenizer_class = get_tokenizer(backend)
        tokenizers[model] = tokenizer_class.build(tokenizer_class.Config(model))

        model_options.append(model)
        memory_usage[model] = (
            embedding_models[model].embeddings.nbytes / 1024 / 1024 / 1024
        )
        memory_usage["total"] += memory_usage[model]

    print(f"Model memory usage:\n{pformat(memory_usage)}")
    print("Embedding models loaded.")

    return embedding_models, tokenizers, model_options
