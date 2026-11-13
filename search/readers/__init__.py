# Each reader yields (pageNumber, text) blocks for one kind of file.
# Modules whose format name is also an importable package or module
# (docx, json, csv) carry a "_file" suffix so the names never clash.
from .pdf import readBlocksFromPdf
from .docx_file import readBlocksFromDocx
from .plain_text import readBlocksFromPlainFile
from .json_file import readBlocksFromJson, jsonPageMeaning
from .xlsx import readBlocksFromXlsx
from .csv_file import readBlocksFromCsv
from .ods import readBlocksFromOds


def pageMeaning(path):
    # Explains what the "page" number means for this kind of file
    extension = path.suffix.lower()
    if extension == ".pdf":
        return "PDF page number"
    if extension == ".docx":
        return "paragraph number"
    if extension == ".json":
        return jsonPageMeaning(path)
    if extension in (".xlsx", ".xlsm", ".ods"):
        return "row number within the sheet named in [brackets]"
    if extension == ".csv":
        return "row number"
    return "starting line of each paragraph (blank-line separated)"


def readBlocks(path):
    # Yields (pageNumber, text) blocks. For files without real pages
    # (docx, plain text, conversation JSON) the number is the paragraph,
    # starting line or speaker-turn index instead.
    extension = path.suffix.lower()

    if extension == ".pdf":
        return readBlocksFromPdf(path)

    if extension == ".docx":
        return readBlocksFromDocx(path)

    if extension == ".json":
        return readBlocksFromJson(path)

    if extension in (".xlsx", ".xlsm"):
        return readBlocksFromXlsx(path)

    if extension == ".csv":
        return readBlocksFromCsv(path)

    if extension == ".ods":
        return readBlocksFromOds(path)

    return readBlocksFromPlainFile(path)
