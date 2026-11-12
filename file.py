from pathlib import Path
from pypdf import PdfReader
from docx import Document
import re

filePath = Path(__file__)

folder = filePath.parent

files = [f.name for f in folder.iterdir() if f.is_file()]

print(files)

fileName = input().strip()
folderName = input().strip()
contentToBeSearched = input().strip()


pattern = re.escape(contentToBeSearched)

def readText(path):
    path = Path(path)
    extension = path.suffix.lower()

    if extension == ".pdf":
        reader = PdfReader(path)
        allText = ""
        for page in reader.pages:
            pageText = page.extract_text()
            if pageText is None:
                pageText = ""
            allText = allText + pageText + "\n"
        return allText

    if extension == ".docx":
        document = Document(path)
        allText = ""
        for paragraph in document.paragraphs:
            allText = allText + paragraph.text + "\n"
        return allText

    # txt, csv, py, etc. are plain text
    return path.read_text(encoding="utf-8")

def openAllFilesAndFindPattern(pattern, targetFolder):
    targetFolder = Path(targetFolder)
    if not targetFolder.is_dir():
        print(f"folder '{targetFolder}' not found")
        return
    for f in sorted(targetFolder.iterdir()):
        if not f.is_file():
            continue
        file = f.name
        try:
            text = readText(f)
        except Exception:
            print(f"{file}: could not be read")
            continue
        hasMatch = bool(re.search(pattern, text))
        if hasMatch:
            print(f"{file}: match found")
        else:
            print(f"{file}: match not found")

def searchForFileInCurrentFolder(file, pattern=None):
    try:
        if file in files:
            if pattern is not None:
                try:
                    text = readText(folder / file)
                except Exception:
                    print(f"{file}: could not be read")
                    return files.index(file)
                if re.search(pattern, text):
                    print(f"{file}: match found")
                else:
                    print(f"{file}: match not found")
            return files.index(file)
        else:
            raise FileNotFoundError
    except FileNotFoundError:
        print("file with this name not found")

def searchForFileInMentionedFolder(folder, file, pattern=None):
    folder = Path(folder)
    if not folder.is_dir():
        print(f"folder '{folder}' not found")
        return
    try:
        for f in folder.iterdir():
            if f.is_file() and f.name == file:
                if pattern is not None:
                    try:
                        text = readText(f)
                    except Exception:
                        print(f"{file}: could not be read")
                        return f
                    if re.search(pattern, text):
                        print(f"{file}: match found")
                    else:
                        print(f"{file}: match not found")
                return f
        raise FileNotFoundError
    except FileNotFoundError:
        print("file with this name not found")

targetFolder = folder / folderName

searchForFileInMentionedFolder(targetFolder, fileName, pattern)
openAllFilesAndFindPattern(pattern, targetFolder)
