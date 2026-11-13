import xml.etree.ElementTree as ElementTree
import zipfile

from ..text import cleanText
from .cells import formatCellValue, joinCells

# An .ods file is a zip holding content.xml; these are the XML namespaces in it
odsNamespaces = {
    "table": "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
    "office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
    "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
}


def odsTag(prefix, name):
    return "{" + odsNamespaces[prefix] + "}" + name


def odsCellText(cell):
    # Same rules as formatCellValue, read from the cell's XML attributes
    valueType = cell.get(odsTag("office", "value-type"))

    if valueType in ("float", "percentage", "currency"):
        return formatCellValue(float(cell.get(odsTag("office", "value"))))

    if valueType == "date":
        dateValue = cell.get(odsTag("office", "date-value"), "")
        # "2026-10-14T00:00:00" -> "2026-10-14", keeps a real time if present
        if dateValue.endswith("T00:00:00"):
            dateValue = dateValue[:10]
        return dateValue.replace("T", " ")

    if valueType == "boolean":
        return cell.get(odsTag("office", "boolean-value"), "").upper()

    # Text (and anything else): join the cell's paragraphs
    paragraphs = []
    for paragraph in cell.iter(odsTag("text", "p")):
        paragraphs.append("".join(paragraph.itertext()))
    return " ".join(paragraphs)


def odsRowCells(row):
    # Cell texts of one row. Empty cells are often stored once with a huge
    # "repeated" count, so a repeated cell is only expanded when it has text.
    cellTexts = []
    for cell in row:
        if cell.tag not in (odsTag("table", "table-cell"), odsTag("table", "covered-table-cell")):
            continue
        text = odsCellText(cell)
        if text.strip() == "":
            continue
        repeatCount = int(cell.get(odsTag("table", "number-columns-repeated"), "1"))
        cellTexts.extend([text] * repeatCount)
    return cellTexts


def readBlocksFromOds(path):
    # Streams content.xml row by row, so a large sheet is never fully in memory
    with zipfile.ZipFile(path) as archive:
        with archive.open("content.xml") as contentFile:
            sheetName = ""
            rowNumber = 0
            for event, element in ElementTree.iterparse(contentFile, events=("start", "end")):
                if event == "start" and element.tag == odsTag("table", "table"):
                    sheetName = element.get(odsTag("table", "name"), "")
                    rowNumber = 0
                    continue

                if event == "end" and element.tag == odsTag("table", "table-row"):
                    repeatCount = int(element.get(odsTag("table", "number-rows-repeated"), "1"))
                    content = joinCells(odsRowCells(element))
                    if content != "":
                        for _ in range(repeatCount):
                            rowNumber += 1
                            yield rowNumber, cleanText("[" + sheetName + "] " + content)
                    else:
                        rowNumber += repeatCount
                    element.clear()

                elif event == "end" and element.tag == odsTag("table", "table"):
                    element.clear()
