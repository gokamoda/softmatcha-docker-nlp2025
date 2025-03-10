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
    line_info: dict[int, str],
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

    for file_idx, (file_path, file_index) in enumerate(
        zip(indexes.paths, indexes.indexes)
    ):
        searcher = SearchIndexInvertedFile(
            file_index, tokenizer, embedding, use_hash=True
        )
        result_htmls = []
        count = 0
        line_count = -1

        result_generator = search_texts(
            pattern,
            file_path,
            searcher,
            tokenizer,
            output_cfg=output_cfg,
            start_line=start_file,
        )
        try:
            for res in result_generator:
                if line_count == -1:
                    line_count = 0
                if line_count == 0:
                    return_dict = {
                        "total_hits": 0,
                        "search_time": stopwatch.timers.elapsed_time["search"],
                        "pattern_length": len(pattern),
                        "pattern_tokenized": tokenizer.decode(pattern_tokens),
                        "result_truncated": False,
                    }
                if line_count + 1 == max_lines:
                    return_dict["result_truncated"] = True
                    break

                result = json.loads(res.text)
                line_number = result["line_number"]
                source_filepath = line_info[str(line_number - 1)]

                file_stem = Path(source_filepath).stem
                paper_identifiers = file_stem.split("-")
                paper_identifier = f"{paper_identifiers[0]}{int(paper_identifiers[1])}-{int(paper_identifiers[2])}"
                if not regex.match(paper_identifier):
                    continue
                count += len(result["matched_token_start_positions"])
                line_count += 1
                nlp_url = f"https://www.anlp.jp/proceedings/annual_meeting/2025/#{paper_identifier}"
                result_html = (
                    "<td><a href='"
                    + nlp_url
                    + "' target='_blank'>"
                    + paper_identifier
                    + "</a> "
                )

                current_position = 0
                for rb_begin, token, score in zip(
                    sum(result["matched_token_start_positions"], []),
                    sum(result["matched_tokens"], []),
                    sum(result["scores"], []),
                ):
                    result_html += (
                        result["original_line"][current_position:rb_begin]
                        + f" <ruby class='text-success'>{result['original_line'][rb_begin : rb_begin + len(token)]}<rt>{score:.2f}&nbsp;</rt></ruby> "
                    )
                    current_position = rb_begin + len(token)
                result_html += result["original_line"][current_position:] + "</td>"
                result_htmls.append(result_html)

                if line_count + 1 == max_lines:
                    return_dict["end_line"] = line_number

        except ValueError:
            "no result found"
            pass

        result_generator.close()

    if line_count == -1:
        return_dict = {
            "total_hits": 0,
            "search_time": stopwatch.timers.elapsed_time["search"],
            "pattern_length": len(pattern),
            "pattern_tokenized": tokenizer.decode(pattern_tokens),
            "result_truncated": False,
            "end_line": -1,
        }

    return_dict["html_lines"] = result_htmls
    return_dict["total_hits"] = count

    return return_dict
