# Prints the readable report, or writes the summary as JSON
import json

from .prompts import askOutputFileName

reportWidth = 70

# How many page/line labels to list before saying "and N more"
maxLabelsShown = 8

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


def printFormBreakdown(termResult, indent):
    # "forms: revenues x3, revenue x2" when a plural/singular or a differently
    # written number was counted; nothing is printed when only the typed
    # spelling was found
    forms = termResult["forms"]
    typed = termResult["term"].replace('"', "").lower()
    if len(forms) == 1 and typed in forms:
        return
    parts = []
    for form, count in sorted(forms.items(), key=lambda item: -item[1]):
        parts.append(form + " x" + str(count))
    print(indent + "    forms: " + ", ".join(parts))


def printTermResult(termResult, indent):
    term = "'" + termResult["term"] + "'"
    if termResult["count"] == 0:
        print(indent + term.ljust(18) + "not found")
        return

    noun = "match" if termResult["count"] == 1 else "matches"
    countText = (str(termResult["count"]) + " " + noun).ljust(13)
    print(indent + term.ljust(18) + countText + formatPageList(termResult["pages"]))
    printFormBreakdown(termResult, indent)
    for snippet in termResult["snippets"]:
        print(indent + "    page " + str(snippet["page"]) + ": " + snippet["text"])


def printReport(summary):
    print()
    print("=" * reportWidth)
    print(" Search : " + summary["search"] + "   (" + modeDescriptions[summary["mode"]] + ")")
    print(" Words  : plurals/singulars also count; a \"quoted\" word matches only as typed")
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
        print("   page = " + fileResult["pageMeans"])
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


def writeOutput(summary, outputFormat, outputFolder):
    # outputFolder is where a JSON file is saved when the user picked that option
    if outputFormat == "json":
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        return

    if outputFormat == "jsonfile":
        outputPath = outputFolder / askOutputFileName()
        with open(outputPath, "w", encoding="utf-8") as outputFile:
            json.dump(summary, outputFile, indent=2, ensure_ascii=False)
        print("saved to " + str(outputPath))
        return

    printReport(summary)
