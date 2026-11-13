import json

from ..text import cleanText
from .plain_text import readBlocksFromPlainFile


def readBlocksFromJson(path):
    # JSON dumped by all_data.py (one item per page, with its page number)
    # or read_conversation.py (one item per speaker turn): each item is one block.
    # Any other JSON layout is searched like a plain text file.
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        yield from readBlocksFromPlainFile(path)
        return

    for itemNumber, item in enumerate(data, start=1):
        if not isinstance(item, dict) or "text" not in item:
            yield itemNumber, cleanText(json.dumps(item, ensure_ascii=False))
            continue
        pageNumber = item["page"] if "page" in item else itemNumber
        yield pageNumber, cleanText(str(item["text"]))


def jsonPageMeaning(path):
    # Looks at the first item to say what a "page" is in this JSON file
    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except Exception:
        return "starting line of each paragraph"
    if not isinstance(data, list):
        return "starting line of each paragraph"
    if data and isinstance(data[0], dict) and "page" in data[0]:
        return "PDF page number stored in the JSON"
    if data and isinstance(data[0], dict) and "speaker" in data[0]:
        return "speaker turn number (the file has no page numbers)"
    return "item number in the JSON list"
