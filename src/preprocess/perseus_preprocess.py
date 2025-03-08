import glob
import os
from typing import List, Union
from xml.dom import minidom

import tqdm
from blingfire import text_to_sentences

OTHER_TEXTUAL_ELEMENTS = {
    "corr",
    "reg",
    "foreign",
    "name",
    "persName",
    "text",
    "body",
    "p",
    "lg",
    "date",
    "dateline",
    "num",
    "q",
    "add",
    "title",
    "placeName",
    "emph",
    "lemma",
    "delSpan",  # probably related to deleted phrases but included in the web main text
    "cit",  # cited line
    "sp",  # spoken lines
    "sic",  # mistaken spelling (OCR?); correct spelling is shown after corr=
    "expan",  # originally abbreviated but expanded?
}
IGNORED_ELEMENTS = {
    "note",
    "pb",
    "milestone",
    "lb",
    "gap",
    "abbr",
    "figure",
    "del",  # deleted in different versions?
    "bibl",  # bibliographical information
    "speaker",  # speaker information
    "anchor",  # corresponds with delSpan tag
}

HIGHLIGHTS = {"italics", "caps"}


def clean(text: str) -> str:
    """Clean text."""
    text = text.replace("\n", " ").strip()
    text = " ".join(text.split())
    return text


def process_lists(node: minidom.Element | minidom.Text) -> list:
    """Process lists."""
    lines = []
    for _node in node.childNodes:
        if _node.nodeType == _node.TEXT_NODE:
            lines.append(clean(_node.data))
    return lines


def process_highlights(node: minidom.Element | minidom.Text) -> list:
    """Process highlights."""
    if node.getAttribute("rend") in HIGHLIGHTS:
        line = []
        for c in node.childNodes:
            if c.nodeType == c.TEXT_NODE:
                line.append(clean(c.data))
            elif c.nodeType == c.ELEMENT_NODE:
                if c.tagName == "hi":
                    line += process_highlights(c)
                elif c.tagName == "quote":
                    line += process_quotes(c)
                elif c.tagName in OTHER_TEXTUAL_ELEMENTS:
                    line.append(process_other(c))
                elif c.tagName in IGNORED_ELEMENTS:
                    continue
                else:
                    print(c.tagName)
                    raise Exception("Unexpected element node")
        return line
    else:
        return ""


def process_other(node: minidom.Element | minidom.Text) -> str:
    """Process other textual info (OTHER_TEXTUAL_ELEMENTS).
    There might be other tags.
    """
    for c in node.childNodes:
        if c.nodeType == c.TEXT_NODE:
            return clean(c.data)
        elif c.nodeType == c.ELEMENT_NODE:
            process_other(c)
        else:
            raise Exception("Unexpected element node")
    return ""


def process_quotes(node: minidom.Element | minidom.Text) -> list:
    """Process quotes."""
    lines = []
    for q in node.childNodes:
        if q.nodeType == q.TEXT_NODE:
            lines.append(clean(q.data))
        elif q.nodeType == q.ELEMENT_NODE:
            if q.tagName == "l":
                lines += process_lists(q)
            elif q.tagName == "hi":
                lines += process_highlights(q)
            elif q.tagName == "quote":
                lines += process_quotes(q)  # recursive?
            elif q.tagName in OTHER_TEXTUAL_ELEMENTS:
                lines += [process_other(q)]
            else:
                if q.tagName in IGNORED_ELEMENTS:
                    continue
                print(q.tagName)
                raise Exception("Unexpected element node")
    return lines


def extract_text(part: minidom.NodeList) -> list:
    """Extract text from a part (<div1>, <div2>, or <p>)."""
    text = []
    for node in part:
        if node.nodeType == node.ELEMENT_NODE:
            if node.tagName == "p":
                for n in node.childNodes:
                    if n.nodeType == n.TEXT_NODE:
                        text.append(clean(n.data))
                    elif n.nodeType == n.ELEMENT_NODE:
                        if n.tagName == "quote":
                            text.append(" ".join(process_quotes(n)))
                        elif n.tagName in OTHER_TEXTUAL_ELEMENTS:
                            text.append(process_other(n))
                        elif n.tagName == "hi":
                            text.append(" ".join(process_highlights(n)))
                        elif n.tagName == "l":
                            text.append(" ".join(process_lists(n)))
                        elif n.tagName in IGNORED_ELEMENTS:
                            continue
                        else:
                            print(n.tagName)
                            raise Exception("Unexpected element node")
            elif node.tagName == "quote":
                text.append(" ".join(process_quotes(node)))
            elif node.tagName in OTHER_TEXTUAL_ELEMENTS:
                text.append(process_other(node))
            elif node.tagName == "hi":
                text.append(" ".join(process_highlights(node)))
            elif node.tagName == "l":
                text.append(" ".join(process_lists(node)))
            elif node.tagName in IGNORED_ELEMENTS:
                continue
            else:
                print(node.tagName)
                raise Exception("Unexpected element node")
        elif node.nodeType == node.TEXT_NODE:
            text.append(clean(node.data))
    text = [t for t in text if t != ""]
    return text


def splitter(text: list) -> list:
    """Split text. Can't split by question marks..."""
    text = " ".join(text).replace("|", "")
    text = [t.strip() for t in text.split(".")]
    return [t.strip() + "." for t in text if t != ""]


def split_sentences(text: list) -> list:
    """Split sentences."""
    text = " ".join(text).replace("|", "")
    return text_to_sentences(text).split("\n")


def extract_book(file_path: str) -> list[list]:
    basename = os.path.basename(file_path)
    print("Extracting", basename)
    texts = []
    document = minidom.parse(file_path)
    for c in document.getElementsByTagName("body")[0].childNodes:
        if c.nodeType == c.ELEMENT_NODE:
            if (
                c.getAttribute("lang") == "en"
            ):  # washington.bio_lat.xml contains the preface in English
                continue
            if c.tagName in {
                "p",
                "l",
                "sp",
            }:  # only sections, like "Florida" by Apuleius (apuleius.fl_lat.xml)
                text = split_sentences(extract_text(c.childNodes))
                print(basename, text)
                texts += text
            else:  # div1, div2, or div3
                for c2 in c.childNodes:
                    if c2.nodeType == c2.ELEMENT_NODE:
                        if c2.tagName in {"p", "sp", "quote", "l"}:
                            text = split_sentences(extract_text(c2.childNodes))
                            print(basename, text)
                            texts += text
                        elif c2.tagName == "div2":
                            for c3 in c2.childNodes:
                                if c3.nodeType == c3.ELEMENT_NODE:
                                    if c3.tagName in {
                                        "p",
                                        "sp",
                                        "quote",
                                        "l",
                                        "cit",
                                    }:
                                        text = split_sentences(
                                            extract_text(c3.childNodes)
                                        )
                                        print(basename, text)
                                        texts += text
                                    elif c3.tagName == "div3":
                                        for c4 in c3.childNodes:
                                            if c4.nodeType == c4.ELEMENT_NODE:
                                                if c4.tagName in {
                                                    "p",
                                                    "sp",
                                                    "quote",
                                                    "l",
                                                    "cit",
                                                }:
                                                    text = split_sentences(
                                                        extract_text(c4.childNodes)
                                                    )
                                                    print(basename, text)
                                                    texts += text
    texts = [t for t in texts if t != ""]
    return texts


def export(outpath: str, texts: list[list]) -> None:
    with open(outpath, "a") as f:
        f.write("\n".join(texts))
        f.write("\n\n")


def main():
    files = glob.glob("lat_text_perseus/*/opensource/*lat.xml")
    print(files)

    outpath = "corpora/lat_text_perseus_preprocessed.txt"
    with open(outpath, "w") as f:
        f.write("")

    for book in tqdm.tqdm(files):
        texts = extract_book(book)
        print("Preview:", texts[0])
        assert texts != [], book
        # dir = "corpora/lat_text_perseus_preprocessed/"
        # if not os.path.exists(dir):
        #     os.makedirs(dir)
        # outpath = os.path.basename(book).replace(".xml", ".txt")
        # outpath = os.path.join(dir, outpath)
        export(outpath, texts)


if __name__ == "__main__":
    main()
