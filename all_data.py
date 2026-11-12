from pathlib import Path
from pypdf import PdfReader
import re
import unicodedata
import json


pageNumberPattern = re.compile(r"^\s*Page \d+ of \d+\s*$", re.IGNORECASE)

# Two or more spaces/tabs in a row, squeezed down to one space
extraSpacesPattern = re.compile(r"[ \t]+")

# A word broken across lines with "-", e.g. "out-of-\npocket"
hyphenBreakPattern = re.compile(r"-\n\s*")

# A single line break inside a paragraph (not a blank line between paragraphs)
singleNewlinePattern = re.compile(r"(?<!\n)\n(?!\n)")

# Three or more line breaks, squeezed down to one blank line
extraNewlinesPattern = re.compile(r"\n{3,}")


def cleanText(text):
    text = unicodedata.normalize("NFKC", text)

    # Drop page number footer lines
    lines = []
    for line in text.splitlines():
        if not pageNumberPattern.match(line):
            lines.append(line.strip())
    text = "\n".join(lines)

    text = extraSpacesPattern.sub(" ", text)
    text = extraNewlinesPattern.sub("\n\n", text)
    # "out-of-\npocket" -> "out-of-pocket"
    text = hyphenBreakPattern.sub("-", text)
    # Wrapped lines inside a paragraph are joined with a space
    text = singleNewlinePattern.sub(" ", text)
    return text.strip()


def readPages(path):
    # Yields (pageNumber, text) one page at a time,
    # so the whole PDF is never held in memory at once
    reader = PdfReader(path)
    for pageNumber, page in enumerate(reader.pages, start=1):
        pageText = page.extract_text()
        if pageText is None:
            pageText = ""
        yield pageNumber, cleanText(pageText)


def main():
    filePath = Path(input("File path: ").strip())
    # Saved next to the PDF, e.g. Q4-TCS-26.pdf -> Q4-TCS-26_all.json
    # (a different name so it does not overwrite read_conversation.py's output)
    jsonPath = filePath.with_name(filePath.stem + "_all.json")

    # Each page is written as soon as it is read
    with open(jsonPath, "w", encoding="utf-8") as jsonFile:
        jsonFile.write("[\n")
        isFirstPage = True
        for pageNumber, text in readPages(filePath):
            if not isFirstPage:
                jsonFile.write(",\n")
            page = {"page": pageNumber, "text": text}
            # ensure_ascii=False keeps characters like ₹ readable
            jsonFile.write("  " + json.dumps(page, ensure_ascii=False))
            isFirstPage = False
        jsonFile.write("\n]\n")

    print("saved to " + str(jsonPath))


main()
