from pypdf import PdfReader

from ..text import cleanText


def readBlocksFromPdf(path):
    # One block per page, so a sentence wrapped over two lines still matches
    reader = PdfReader(path)
    for pageNumber, page in enumerate(reader.pages, start=1):
        pageText = page.extract_text()
        if pageText is None:
            continue
        yield pageNumber, cleanText(pageText)
