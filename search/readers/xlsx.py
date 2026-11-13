from openpyxl import load_workbook

from ..text import cleanText
from .cells import formatCellValue, joinCells


def readBlocksFromXlsx(path):
    # One block per row: (row number, "[Sheet name] a | b | c").
    # read_only streams one row at a time; data_only gives the computed
    # value of a formula cell instead of the formula text.
    workbook = load_workbook(path, read_only=True, data_only=True)
    try:
        for sheet in workbook.worksheets:
            prefix = "[" + sheet.title + "] "
            for rowNumber, row in enumerate(sheet.iter_rows(values_only=True), start=1):
                cellTexts = []
                for value in row:
                    cellTexts.append(formatCellValue(value))
                content = joinCells(cellTexts)
                if content != "":
                    yield rowNumber, cleanText(prefix + content)
    finally:
        workbook.close()
