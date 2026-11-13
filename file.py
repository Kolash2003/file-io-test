from pathlib import Path
from pypdf import PdfReader
from docx import Document
import re
import unicodedata
import json

scriptFolder = Path(__file__).parent

# Any run of spaces, tabs or newlines is squeezed down to one space
whitespacePattern = re.compile(r"\s+")

# Gap allowed between two words of the search text:
# spaces, tabs, newlines or hyphens (so "out-of- pocket" still matches "out of pocket")
wordGap = r"[\s\-‐-―]+"

# Punctuation stripped from the ends of what the user typed, e.g. "profit." -> "profit"
edgePunctuation = ".,;:!?\"'()[]{}"

# How many characters of context to show on each side of a match
snippetContext = 40

# How many snippets to print per file
maxSnippetsPerFile = 3

# How many page/line labels to list before saying "and N more"
maxLabelsShown = 8


def cleanText(text):
    # NFKC turns special PDF characters like "ﬁ" into normal "fi",
    # so searching for "five" also finds "ﬁve"
    text = unicodedata.normalize("NFKC", text)
    return whitespacePattern.sub(" ", text).strip()


def readBlocksFromPdf(path):
    # One block per page, so a sentence wrapped over two lines still matches
    reader = PdfReader(path)
    for pageNumber, page in enumerate(reader.pages, start=1):
        pageText = page.extract_text()
        if pageText is None:
            continue
        yield pageNumber, cleanText(pageText)


def readBlocksFromDocx(path):
    document = Document(path)
    for paragraphNumber, paragraph in enumerate(document.paragraphs, start=1):
        yield paragraphNumber, cleanText(paragraph.text)


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

    return readBlocksFromPlainFile(path)


def splitIntoWords(text):
    words = []
    for word in text.split():
        word = word.strip(edgePunctuation)
        if word != "":
            words.append(word)
    return words


def buildPattern(words):
    # Words joined by a flexible gap, wrapped so only whole words match:
    # "tcs" matches "TCS" and "TCS." but not "etcsomething"
    escapedWords = []
    for word in words:
        escapedWords.append(re.escape(word))
    body = wordGap.join(escapedWords)
    return re.compile(r"(?<!\w)" + body + r"(?!\w)", re.IGNORECASE)


def makeSnippet(text, start, end):
    snippetStart = max(0, start - snippetContext)
    snippetEnd = min(len(text), end + snippetContext)
    snippet = text[snippetStart:snippetEnd]
    if snippetStart > 0:
        snippet = "..." + snippet
    if snippetEnd < len(text):
        snippet = snippet + "..."
    return snippet


def findMatches(path, compiledPatterns):
    # Returns one result per pattern:
    # {"count": 3, "pages": [1, 2], "snippets": [{"page": 1, "text": "..."}, ...]}
    results = []
    for _ in compiledPatterns:
        results.append({"count": 0, "pages": [], "snippets": []})

    for pageNumber, text in readBlocks(path):
        for index, compiledPattern in enumerate(compiledPatterns):
            result = results[index]
            for match in compiledPattern.finditer(text):
                result["count"] += 1
                if pageNumber not in result["pages"]:
                    result["pages"].append(pageNumber)
                if len(result["snippets"]) < maxSnippetsPerFile:
                    snippet = makeSnippet(text, match.start(), match.end())
                    result["snippets"].append({"page": pageNumber, "text": snippet})
    return results


def searchFile(path, searchMode, words):
    # Returns one dictionary describing the result for this file:
    # {"file": "x.pdf", "found": True, "terms": [{"term": "tcs", "count": 3, ...}]}
    # or {"file": "x.pdf", "error": "could not be read"}
    if searchMode == "phrase":
        terms = [" ".join(words)]
        patterns = [buildPattern(words)]
    else:
        terms = words
        patterns = []
        for word in words:
            patterns.append(buildPattern([word]))

    try:
        results = findMatches(path, patterns)
    except Exception:
        return {"file": path.name, "error": "could not be read"}

    termResults = []
    foundCount = 0
    for term, result in zip(terms, results):
        termResult = {"term": term}
        termResult.update(result)
        termResults.append(termResult)
        if result["count"] > 0:
            foundCount += 1

    if searchMode == "all":
        found = foundCount == len(terms)
    else:
        found = foundCount > 0

    return {"file": path.name, "found": found, "terms": termResults}


def searchOneFile(targetFolder, fileName, searchMode, words):
    filePath = targetFolder / fileName

    if filePath.is_file():
        return [searchFile(filePath, searchMode, words)]

    print("file '" + fileName + "' not found in '" + str(targetFolder) + "'")
    return []


def searchAllFiles(targetFolder, searchMode, words):
    fileResults = []
    for item in sorted(targetFolder.iterdir()):
        if item.is_file():
            fileResults.append(searchFile(item, searchMode, words))
    return fileResults


def getFileNamesInFolder(targetFolder):
    fileNames = []
    for item in targetFolder.iterdir():
        if item.is_file():
            fileNames.append(item.name)
    fileNames.sort()
    return fileNames


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

reportWidth = 70

modeDescriptions = {
    "phrase": "exact phrase",
    "any": "any of the words",
    "all": "all of the words",
}


def formatPageList(pages):
    # e.g. "pages 1, 2, 4 (+21 more)"
    shown = []
    for pageNumber in pages[:maxLabelsShown]:
        shown.append(str(pageNumber))
    text = ("pages " if len(pages) > 1 else "page ") + ", ".join(shown)
    if len(pages) > maxLabelsShown:
        text = text + " (+" + str(len(pages) - maxLabelsShown) + " more)"
    return text


def printTermResult(termResult, indent):
    term = "'" + termResult["term"] + "'"
    if termResult["count"] == 0:
        print(indent + term.ljust(18) + "not found")
        return

    noun = "match" if termResult["count"] == 1 else "matches"
    countText = (str(termResult["count"]) + " " + noun).ljust(13)
    print(indent + term.ljust(18) + countText + formatPageList(termResult["pages"]))
    for snippet in termResult["snippets"]:
        print(indent + "    page " + str(snippet["page"]) + ": " + snippet["text"])


def printReport(summary):
    print()
    print("=" * reportWidth)
    print(" Search : \"" + summary["search"] + "\"   (" + modeDescriptions[summary["mode"]] + ")")
    print(" Folder : " + summary["folder"])
    print(" Files  : " + str(len(summary["results"])) + " searched")
    print("=" * reportWidth)

    notFound = []
    unreadable = []
    for fileResult in summary["results"]:
        if "error" in fileResult:
            unreadable.append(fileResult["file"])
            continue
        if not fileResult["found"]:
            notFound.append(fileResult["file"])
            continue

        print()
        print(" " + fileResult["file"].ljust(reportWidth - 10, ".") + " FOUND")
        for termResult in fileResult["terms"]:
            printTermResult(termResult, "   ")

    print()
    print("-" * reportWidth)
    print(" Matched   : " + str(len(summary["results"]) - len(notFound) - len(unreadable))
          + " of " + str(len(summary["results"])) + " files")
    if notFound:
        print(" No match  : " + ", ".join(notFound))
    if unreadable:
        print(" Unreadable: " + ", ".join(unreadable))
    print("-" * reportWidth)


def askOutputFormat():
    print("Show results as:")
    print("  1) readable report")
    print("  2) JSON on screen")
    print("  3) JSON saved to a file")
    choice = input("Choice (1/2/3, default 1): ").strip()
    if choice == "2":
        return "json"
    if choice == "3":
        return "jsonfile"
    return "report"


def writeOutput(summary, outputFormat):
    if outputFormat == "json":
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        return

    if outputFormat == "jsonfile":
        defaultName = "search_results.json"
        fileName = input("Save as (default " + defaultName + "): ").strip()
        if fileName == "":
            fileName = defaultName
        outputPath = scriptFolder / fileName
        with open(outputPath, "w", encoding="utf-8") as outputFile:
            json.dump(summary, outputFile, indent=2, ensure_ascii=False)
        print("saved to " + str(outputPath))
        return

    printReport(summary)


def askSearchMode(words):
    # Only asked when the user typed more than one word
    if len(words) == 1:
        return "phrase"

    print("You entered " + str(len(words)) + " words. Search for:")
    print("  1) the exact sentence/phrase")
    print("  2) any of the words")
    print("  3) all of the words (anywhere in the file)")
    choice = input("Choice (1/2/3, default 1): ").strip()

    if choice == "2":
        return "any"
    if choice == "3":
        return "all"
    return "phrase"


def main():
    folderName = input("Folder to search (leave blank for this folder): ")
    folderName = folderName.strip()
    targetFolder = scriptFolder / folderName

    if not targetFolder.is_dir():
        print("folder '" + str(targetFolder) + "' not found")
        return

    fileNames = getFileNamesInFolder(targetFolder)
    print("Files in this folder:", fileNames)

    fileName = input("File name (leave blank to search all files): ")
    fileName = fileName.strip()

    contentToBeSearched = input("Text to search for: ")
    words = splitIntoWords(cleanText(contentToBeSearched))

    if not words:
        print("search text cannot be empty")
        return

    searchMode = askSearchMode(words)
    outputFormat = askOutputFormat()

    if fileName == "":
        fileResults = searchAllFiles(targetFolder, searchMode, words)
    else:
        fileResults = searchOneFile(targetFolder, fileName, searchMode, words)

    if not fileResults:
        return

    summary = {
        "search": " ".join(words),
        "mode": searchMode,
        "folder": str(targetFolder),
        "results": fileResults,
    }
    writeOutput(summary, outputFormat)


main()
