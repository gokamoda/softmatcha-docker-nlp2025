#!/usr/bin/env python3
import json
import re
from argparse import Namespace
from collections import defaultdict
from typing import Any, TypeVar

import numpy as np
from softmatcha import configs, stopwatch
from softmatcha.cli.search_inverted_index import Statistics, search_texts
from softmatcha.search import Search, SearchIndex, SearchIndexInvertedFile
from softmatcha.struct import Pattern
from softmatcha.struct.index_inverted import IndexInvertedFileCollection
from pathlib import Path

output_cfg = Namespace(
    json=True,
    profile=True,
    log=None,
    line_number=False,
    with_filename=False,
    no_filename=True,
    only_matching=False,
    quiet=False,
)


def get_formatted_search_result(
    pattern: str,
    tokenizer: Any,
    embedding: Any,
    threshold: float,
    indexes: IndexInvertedFileCollection,
    start_file: int = 0,
    max_lines: int = 250,
    filter_regex: str = ".*",
):
    regex = re.compile(filter_regex)

    stopwatch.timers.reset(profile=output_cfg.profile)
    pattern_tokens = tokenizer(pattern)
    pattern_embeddings = embedding(pattern_tokens)
    pattern = Pattern.build(
        pattern_tokens,
        pattern_embeddings,
        [threshold] * len(pattern_embeddings),
    )

    return_dict = {
        "total_hits": 0,
        "num_searched_files": 0,
        "search_time": 0,
        "pattern_length": len(pattern),
        "pattern_tokenized": tokenizer.decode(pattern_tokens),
        "result_truncated": False,
    }
    result_htmls = []

    for file_idx, (file_path, file_index) in enumerate(zip(indexes.paths, indexes.indexes)):
        if file_idx < start_file:
            continue

        file_stem = Path(file_path).stem
        paper_identifiers = file_stem.split("-")
        nlp_url = f"https://www.anlp.jp/proceedings/annual_meeting/2025/#{file_identifiers[0]}{int(file_identifiers[1])}-{int(file_identifiers[2])}"

        if not regex.match(file_stem):
            continue


        if return_dict["total_hits"] >= max_lines:
            return_dict["result_truncated"] = True
            return_dict["end_line"] = file_idx
            break
        searcher = SearchIndexInvertedFile(
            file_index, tokenizer, embedding, use_hash=True
        )

        
        Statistics(0, 0)
        count = -1

        result_generator = search_texts(
            pattern,
            file_path,
            searcher,
            tokenizer,
            output_cfg=output_cfg,
            start_line=0,
        )
        try:
            for count, res in enumerate(result_generator):
                if count == 0:
                    return_dict["total_hits"] += res.stats.num_hit_spans
                    return_dict["num_searched_files"] += 1
                    return_dict["search_time"] += stopwatch.timers.elapsed_time["search"]

                result = json.loads(res.text)
                result_html = "<td><a href='" + nlp_url + "' target='_blank'>" + file_stem + "</a> "

                current_position = 0
                for rb_begin, token, score in zip(
                    sum(result["matched_token_start_positions"], []),
                    sum(result["matched_tokens"], []),
                    sum(result["scores"], []),
                ):
                    result_html += (
                        result["original_line"][current_position:rb_begin]
                        + f" <ruby class='text-success'>{result['original_line'][rb_begin:rb_begin + len(token)]}<rt>{score:.2f}&nbsp;</rt></ruby> "
                    )
                    current_position = rb_begin + len(token)
                result_html += result["original_line"][current_position:] + "</td>"
                result_htmls.append(result_html)

        except ValueError:
            "no result found"
            pass

        result_generator.close()

    # if count == -1:
    #     return_dict = {
    #         "total_hits": 0,
    #         "search_time": stopwatch.timers.elapsed_time["search"],
    #         "pattern_length": len(pattern),
    #         "pattern_tokenized": tokenizer.decode(pattern_tokens),
    #         "result_truncated": False,
    #         "end_line": -1,
    #     }

    return_dict["html_lines"] = result_htmls
    print(return_dict['result_truncated'])

    return return_dict
