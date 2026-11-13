from docx import Document

from ..text import cleanText


def readBlocksFromDocx(path):
    document = Document(path)
    for paragraphNumber, paragraph in enumerate(document.paragraphs, start=1):
        yield paragraphNumber, cleanText(paragraph.text)
