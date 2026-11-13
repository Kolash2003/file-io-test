import re
import unicodedata

# Any run of spaces, tabs or newlines is squeezed down to one space
whitespacePattern = re.compile(r"\s+")


def cleanText(text):
    # NFKC turns special PDF characters like "ﬁ" into normal "fi",
    # so searching for "five" also finds "ﬁve"
    text = unicodedata.normalize("NFKC", text)
    return whitespacePattern.sub(" ", text).strip()
