# Turns what the user typed into search words and the regex that finds them
import re

# Gap allowed between two words of the search text: spaces, tabs, newlines,
# hyphens (so "out-of- pocket" still matches "out of pocket") and the " | "
# that separates spreadsheet cells (so "net profit" matches "Net | profit")
wordGap = r"[\s\-‐-―|]+"
wordGapPattern = re.compile(wordGap)

# Text inside double quotes (straight or curly) is matched exactly as typed:
# "revenue" finds revenue but not revenues
quotedPattern = re.compile(r'["“”]([^"“”]*)["“”]')

vowels = "aeiou"

# Punctuation stripped from the ends of what the user typed, e.g. "profit." -> "profit"
edgePunctuation = ".,;:!?\"'()[]{}"

# A plain number as typed by the user, e.g. "73188", "73,188" or "2.8"
numberPattern = re.compile(r"\d[\d,]*(?:\.\d+)?")


def splitIntoWords(text):
    words = []
    for word in text.split():
        word = word.strip(edgePunctuation)
        if word != "":
            words.append(word)
    return words


def parseSearchText(text):
    # Splits what the user typed into words, each {"text": "revenue", "exact": False}.
    # Words inside double quotes are exact; all other words also match their
    # plural/singular spellings. An unmatched quote is treated as punctuation.
    words = []
    position = 0
    for match in quotedPattern.finditer(text):
        for word in splitIntoWords(text[position:match.start()]):
            words.append({"text": word, "exact": False})
        for word in splitIntoWords(match.group(1)):
            words.append({"text": word, "exact": True})
        position = match.end()
    for word in splitIntoWords(text[position:]):
        words.append({"text": word, "exact": False})
    return words


def termLabel(words):
    # How a term is shown in the report: net "profit"  (quotes mark an exact word)
    parts = []
    for word in words:
        if word["exact"]:
            parts.append('"' + word["text"] + '"')
        else:
            parts.append(word["text"])
    return " ".join(parts)


def singularForms(word):
    # Possible singulars of a typed word: revenues -> revenue, companies -> company,
    # losses -> loss, taxes -> tax, halves -> half. A wrong guess is harmless:
    # a form only counts when it actually appears in a file.
    forms = []
    if word.endswith("ies") and len(word) > 4:
        forms.append(word[:-3] + "y")
    if word.endswith("ves") and len(word) > 4:
        forms.append(word[:-3] + "f")
        forms.append(word[:-3] + "fe")
    if word.endswith(("sses", "shes", "ches", "xes", "zes", "oes")):
        forms.append(word[:-2])
    if word.endswith("s") and not word.endswith("ss"):
        forms.append(word[:-1])
    # Very short stems ("gas" -> "ga") would match unrelated words, so skip them
    kept = []
    for form in forms:
        if len(form) >= 3:
            kept.append(form)
    return kept


def pluralForms(word):
    # Plurals of a singular: company -> companies, loss -> losses,
    # half -> halves, tax -> taxes, revenue -> revenues
    forms = []
    if word.endswith("y") and len(word) > 1 and word[-2] not in vowels:
        forms.append(word[:-1] + "ies")
    if word.endswith("fe"):
        forms.append(word[:-2] + "ves")
    elif word.endswith("f"):
        forms.append(word[:-1] + "ves")
    if word.endswith(("s", "x", "z", "ch", "sh", "o")):
        forms.append(word + "es")
    forms.append(word + "s")
    return forms


def wordForms(word):
    # Every spelling a typed word may have in a file, the typed one first.
    # Only plain words get variants; numbers and mixed words like "q2" or
    # "covid-19" are left exactly as typed.
    if not word.isalpha():
        return [word]
    lower = word.lower()
    bases = [lower] + singularForms(lower)
    forms = []
    for base in bases:
        for form in [base] + pluralForms(base):
            if form not in forms:
                forms.append(form)
    return forms


def escapeWord(word):
    # A number matches with or without thousands separators:
    # "73188" or "73,188" both find "73188", "73,188" and "₹73,188"
    if numberPattern.fullmatch(word):
        wholePart, dot, fraction = word.partition(".")
        digits = wholePart.replace(",", "")
        body = ",?".join(digits)
        if dot:
            body = body + r"\." + fraction
        return body
    return re.escape(word)


def wordPattern(word):
    # Regex for one typed word. An exact word is used as typed; any other word
    # becomes an alternation of its spellings: (?:revenues|revenue)
    if word["exact"]:
        return escapeWord(word["text"])
    forms = wordForms(word["text"])
    if len(forms) == 1:
        return escapeWord(forms[0])
    forms.sort(key=len, reverse=True)
    escapedForms = []
    for form in forms:
        escapedForms.append(re.escape(form))
    return "(?:" + "|".join(escapedForms) + ")"


def buildPattern(words):
    # Words joined by a flexible gap, wrapped so only whole words match:
    # "tcs" matches "TCS" and "TCS." but not "etcsomething"
    escapedWords = []
    for word in words:
        escapedWords.append(wordPattern(word))
    body = wordGap.join(escapedWords)
    return re.compile(r"(?<!\w)" + body + r"(?!\w)", re.IGNORECASE)
