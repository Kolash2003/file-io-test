from pathlib import Path
from pypdf import PdfReader
import re
import unicodedata
import json

nameWord = r"(?:(?:Mr|Ms|Mrs|Dr)\.|[A-Z][a-zA-Z'\-]+|[A-Z]\.?)"
speakerLinePattern = re.compile(
    r"^\s*"
    r"(?P<speaker>" + nameWord + r"(?:\s+" + nameWord + r"){0,4}(?:\s*\([^)]*\))?)"
    r"\s*:\s*"
    r"(?P<text>.*)$"
)

# Labels that look like "Name:" but are parts of the document, not people.
notSpeakers = {"sub", "subject", "encl", "note", "ref", "date", "to", "from",
               "tel", "fax", "email", "website", "disclaimer"}

# Footer lines such as "Page 3 of 34" that should not be part of anyone's speech
pageNumberPattern = re.compile(r"^Page \d+ of \d+$", re.IGNORECASE)


def readLinesFromPdf(path):
    reader = PdfReader(path)
    for page in reader.pages:
        pageText = page.extract_text()
        if pageText is None:
            continue
        # NFKC turns special PDF characters like "ﬁ" into normal "fi",
        # so searching for "five" also finds "ﬁve"
        pageText = unicodedata.normalize("NFKC", pageText)
        for line in pageText.splitlines():
            yield line


def joinLines(lines):
    # Joins wrapped lines with spaces, except when a line ends with "-",
    # so "out-of-" + "pocket" becomes "out-of-pocket" not "out-of- pocket"
    text = ""
    for line in lines:
        if text == "" or text.endswith("-"):
            text = text + line
        else:
            text = text + " " + line
    return text


def readSpeakerTurns(path):
    # Yields (speaker, text) for each turn of the conversation.
    # Lines without a "Name:" at the start belong to whoever spoke last,
    # because a long answer usually wraps over many lines/pages.
    # Only one turn is kept in memory at a time.
    currentSpeaker = None
    currentLines = []

    for line in readLinesFromPdf(path):
        line = line.strip()
        if line == "" or pageNumberPattern.match(line):
            continue

        match = speakerLinePattern.match(line)
        if match is not None and match.group("speaker").lower() in notSpeakers:
            match = None

        if match is not None:
            # A new speaker started, so hand back the previous turn first
            if currentSpeaker is not None:
                yield currentSpeaker, joinLines(currentLines)
            currentSpeaker = match.group("speaker").strip()
            currentLines = [match.group("text")]
        elif currentSpeaker is not None:
            currentLines.append(line)
        # Text before the first speaker (title, date, etc.) is skipped

    if currentSpeaker is not None:
        yield currentSpeaker, joinLines(currentLines)


def main():
    filePath = Path(input("File path: ").strip())
    # Saved next to the PDF with the same name, e.g. Q4-TCS-26.pdf -> Q4-TCS-26.json
    jsonPath = filePath.with_suffix(".json")

    # Each turn is written as soon as it is read, so the whole
    # conversation is never held in memory at once
    with open(jsonPath, "w", encoding="utf-8") as jsonFile:
        jsonFile.write("[\n")
        isFirstTurn = True
        for speaker, text in readSpeakerTurns(filePath):
            if not isFirstTurn:
                jsonFile.write(",\n")
            turn = {"speaker": speaker, "text": text}
            # ensure_ascii=False keeps characters like ₹ readable
            jsonFile.write("  " + json.dumps(turn, ensure_ascii=False))
            isFirstTurn = False
        jsonFile.write("\n]\n")

    print("saved to " + str(jsonPath))


main()
