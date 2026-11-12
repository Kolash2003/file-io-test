from pathlib import Path
from pypdf import PdfReader
from docx import Document
import re

scriptFolder = Path(__file__).parent


# Each readLines... function uses "yield" to hand back one line at a time,
# so the whole file's text is never joined into one big string.

def readLinesFromPdf(path):
    reader = PdfReader(path)
    # Pages are extracted one at a time, then split into lines
    for page in reader.pages:
        pageText = page.extract_text()
        if pageText is None:
            continue
        for line in pageText.splitlines():
            yield line


def readLinesFromDocx(path):
    document = Document(path)
    for paragraph in document.paragraphs:
        yield paragraph.text


def readLinesFromPlainFile(path):
    # txt, csv, py, etc. are plain text files.
    # Looping over the file object reads it one line at a time.
    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            yield line


def readLines(path):
    extension = path.suffix.lower()

    if extension == ".pdf":
        return readLinesFromPdf(path)

    if extension == ".docx":
        return readLinesFromDocx(path)

    return readLinesFromPlainFile(path)


def checkFileForPattern(path, pattern):
    # Compile once so the pattern isn't re-processed for every line
    compiledPattern = re.compile(pattern)

    try:
        # Check each line and stop as soon as one matches
        for line in readLines(path):
            if compiledPattern.search(line) is not None:
                print(path.name + ": match found")
                return
    except Exception:
        print(path.name + ": could not be read")
        return

    print(path.name + ": match not found")


def searchOneFile(targetFolder, fileName, pattern):
    filePath = targetFolder / fileName

    if filePath.is_file():
        checkFileForPattern(filePath, pattern)
    else:
        print("file '" + fileName + "' not found in '" + str(targetFolder) + "'")


def searchAllFiles(targetFolder, pattern):
    allItems = sorted(targetFolder.iterdir())

    for item in allItems:
        if item.is_file():
            checkFileForPattern(item, pattern)


def getFileNamesInFolder(targetFolder):
    fileNames = []
    for item in targetFolder.iterdir():
        if item.is_file():
            fileNames.append(item.name)
    fileNames.sort()
    return fileNames


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
    contentToBeSearched = contentToBeSearched.strip()

    if contentToBeSearched == "":
        print("search text cannot be empty")
        return

    pattern = re.escape(contentToBeSearched)

    if fileName == "":
        searchAllFiles(targetFolder, pattern)
    else:
        searchOneFile(targetFolder, fileName, pattern)


main()
