# Runs the search patterns over the blocks of a file and collects the results
from .readers import readBlocks, pageMeaning
from .terms import wordGapPattern, termLabel, buildPattern

# How many characters of context to show on each side of a match
snippetContext = 40

# Spreadsheet rows start with "[Sheet name] "; a prefix longer than this
# is treated as ordinary text, not a sheet name
maxSheetPrefixLength = 64

# How many snippets to keep per file
maxSnippetsPerFile = 3


def sheetPrefix(text):
    # "[Q2 Data] TCS | 73188" -> "[Q2 Data] ", or "" when there is no prefix
    if not text.startswith("["):
        return ""
    prefixEnd = text.find("] ")
    if prefixEnd == -1 or prefixEnd > maxSheetPrefixLength:
        return ""
    return text[:prefixEnd + 2]


def makeSnippet(text, start, end):
    snippetStart = max(0, start - snippetContext)
    snippetEnd = min(len(text), end + snippetContext)
    snippet = text[snippetStart:snippetEnd]
    prefix = sheetPrefix(text)
    if snippetStart > len(prefix):
        # Keep the sheet name visible even when the match is far into the row
        snippet = prefix + "..." + snippet
    elif snippetStart > 0:
        snippet = "..." + snippet
    if snippetEnd < len(text):
        snippet = snippet + "..."
    return snippet


def matchedForm(matchText):
    # "Net | Profits" -> "net profits", so one wording is counted once in the breakdown
    return wordGapPattern.sub(" ", matchText).lower()


def findMatches(path, compiledPatterns):
    # Returns one result per pattern:
    # {"count": 3, "pages": [1, 2], "forms": {"revenue": 2, "revenues": 1},
    #  "snippets": [{"page": 1, "text": "..."}, ...]}
    results = []
    for _ in compiledPatterns:
        results.append({"count": 0, "pages": [], "forms": {}, "snippets": []})

    for pageNumber, text in readBlocks(path):
        for index, compiledPattern in enumerate(compiledPatterns):
            result = results[index]
            for match in compiledPattern.finditer(text):
                result["count"] += 1
                form = matchedForm(match.group())
                result["forms"][form] = result["forms"].get(form, 0) + 1
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
        terms = [termLabel(words)]
        patterns = [buildPattern(words)]
    else:
        terms = []
        patterns = []
        for word in words:
            terms.append(termLabel([word]))
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

    return {
        "file": path.name,
        "pageMeans": pageMeaning(path),
        "found": found,
        "terms": termResults,
    }


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
