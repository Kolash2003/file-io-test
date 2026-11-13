import csv

from ..text import cleanText
from .cells import joinCells


def readBlocksFromCsv(path):
    # One block per row, numbered by row. No sheet prefix, a CSV has no sheets.
    with open(path, "r", encoding="utf-8", newline="") as file:
        for rowNumber, row in enumerate(csv.reader(file), start=1):
            content = joinCells(row)
            if content != "":
                yield rowNumber, cleanText(content)
