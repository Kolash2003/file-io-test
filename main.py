# Entry point: run with  python main.py
from pathlib import Path

from search.text import cleanText
from search.terms import parseSearchText, termLabel
from search.matching import searchOneFile, searchAllFiles, getFileNamesInFolder
from search.prompts import askSearchMode, askOutputFormat
from search.report import writeOutput

# Folders typed at the prompt are relative to this file, and JSON results are saved beside it
scriptFolder = Path(__file__).parent


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
    words = parseSearchText(cleanText(contentToBeSearched))

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
        "search": termLabel(words),
        "mode": searchMode,
        "folder": str(targetFolder),
        "results": fileResults,
    }
    writeOutput(summary, outputFormat, scriptFolder)


if __name__ == "__main__":
    main()
