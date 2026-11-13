# The questions asked on the terminal


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


def askOutputFileName():
    defaultName = "search_results.json"
    fileName = input("Save as (default " + defaultName + "): ").strip()
    if fileName == "":
        return defaultName
    return fileName
