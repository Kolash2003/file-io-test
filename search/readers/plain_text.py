from ..text import cleanText


def readBlocksFromPlainFile(path):
    # One block per paragraph (lines separated by a blank line),
    # labelled with the line it starts on. Only one paragraph is held in memory.
    with open(path, "r", encoding="utf-8") as file:
        currentLines = []
        startLine = 1
        for lineNumber, line in enumerate(file, start=1):
            if line.strip() == "":
                if currentLines:
                    yield startLine, cleanText(" ".join(currentLines))
                    currentLines = []
                startLine = lineNumber + 1
            else:
                currentLines.append(line)
        if currentLines:
            yield startLine, cleanText(" ".join(currentLines))
