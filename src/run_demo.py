import json
from argparse import Namespace

import psutil
from fastapi import Request
from fastapi.responses import HTMLResponse, JSONResponse

from config import SoftMatchaAPI, get_model_tokenizers
from mylogger import init_logging
from search import get_formatted_search_result

LOG_PATH = "log.jsonl"
logger = init_logging("app", LOG_PATH)

app = SoftMatchaAPI()

embedding_models, tokenizers, model_options = get_model_tokenizers(
    app.embedding_model_infos
)
indexes = app.load_indexes()


def check_model_availability(
    corpus_name, model_name, corpus_model_combinations, embedding_model_infos
):
    if corpus_name not in corpus_model_combinations:
        raise ValueError(f"Corpus {corpus_name} not found in the index.")

    if model_name not in corpus_model_combinations[corpus_name]:
        raise ValueError(f"Model {model_name} not found in the index.")

    backend = embedding_model_infos[model_name]
    return model_name, backend


@app.get("/", response_class=HTMLResponse)
def index(
    request: Request,
    threshold: float = 0.5,
    query: str = "",
    corpus_model="NLP2025_ja | fasttext-ja-vectors",
    filter_regex: str = ".*"
):
    return app.templates.TemplateResponse(
        "top.html",
        {
            "request": request,
            "threshold": threshold,
            "query": query,
            "corpus_model": corpus_model,
            "corpus_model_options": app.corpus_model_options,
            "filter_regex": filter_regex,
        },
    )


@app.get("/search", response_class=JSONResponse)
def search_demo(
    request: Request,
    threshold: float = 0.5,
    query: str = "",
    corpus_model="NLP2025_ja | fasttext-ja-vectors",
    start: int = 0,
    filter_regex: str = ".*",
):
    corpus, model_name = corpus_model.split(" | ")

    try:
        model_name, _ = check_model_availability(
            corpus_name=corpus,
            model_name=model_name,
            corpus_model_combinations=app.corpus_model_combinations,
            embedding_model_infos=app.embedding_model_infos,
        )
    except ValueError as e:
        print(e)
        return JSONResponse(
            content={
                "error": str(e),
            }
        )

    if threshold < 0 or threshold > 1:
        return JSONResponse(
            content={
                "error": "Threshold must be between 0 and 1.",
            }
        )

    args_dict = {
        "threshold": threshold,
        "pattern": query,
        "start_file": start,
        "max_lines": 100,
        "filter_regex": filter_regex,
    }

    results = get_formatted_search_result(
        **args_dict,
        embedding=embedding_models[model_name],
        tokenizer=tokenizers[model_name],
        indexes=indexes[corpus],
    )

    logger.info(
        json.dumps(
            {
                "query": query,
                "threshold": threshold,
                "search_time": results["search_time"],
                "pattern_length": results["pattern_length"],
                "pattern_tokenized": results["pattern_tokenized"],
                # "memory_usage": psutil.virtual_memory().active / 1024**3,
                "memory_usage": (
                    psutil.virtual_memory().total - psutil.virtual_memory().available
                )
                / 1024**3,
                "result_truncated": results["result_truncated"],
            },
            ensure_ascii=False,
        )
    )

    return JSONResponse(content={"result": results})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)