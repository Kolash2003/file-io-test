# Helpers shared by the spreadsheet readers (xlsx, csv, ods)
from datetime import datetime, date


def formatCellValue(value):
    # Turns a cell value into search text:
    # 73188.0 -> "73188", 2.8 -> "2.8", a date -> "2026-10-14", empty -> ""
    if value is None:
        return ""
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, datetime):
        if value.hour == 0 and value.minute == 0 and value.second == 0:
            return value.strftime("%Y-%m-%d")
        return value.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(value, date):
        return value.strftime("%Y-%m-%d")
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def joinCells(cellTexts):
    # "TCS | 73188 | 2.8" with empty cells left out
    parts = []
    for text in cellTexts:
        text = text.strip()
        if text != "":
            parts.append(text)
    return " | ".join(parts)
