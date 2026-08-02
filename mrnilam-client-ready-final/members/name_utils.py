import re


VOWELS = {
    "अ": "a", "आ": "a", "इ": "i", "ई": "i",
    "उ": "u", "ऊ": "u", "ए": "e", "ऐ": "ai",
    "ओ": "o", "औ": "au", "ऋ": "ri",
}

MATRAS = {
    "ा": "a",
    "ि": "i",
    "ी": "i",
    "ु": "u",
    "ू": "u",
    "े": "e",
    "ै": "ai",
    "ो": "o",
    "ौ": "au",
    "ृ": "ri",
}

CONSONANTS = {
    "क": "k", "ख": "kh", "ग": "g", "घ": "gh", "ङ": "ng",
    "च": "ch", "छ": "chh", "ज": "j", "झ": "jh", "ञ": "ny",
    "ट": "t", "ठ": "th", "ड": "d", "ढ": "dh", "ण": "n",
    "त": "t", "थ": "th", "द": "d", "ध": "dh", "न": "n",
    "प": "p", "फ": "ph", "ब": "b", "भ": "bh", "म": "m",
    "य": "y", "र": "r", "ल": "l", "व": "v",
    "श": "sh", "ष": "sh", "स": "s", "ह": "h",
    "ळ": "l",
}

VIRAMA = "्"
ANUSVARA = {"ं": "n", "ँ": "n", "ः": "h"}


def is_devanagari(text):
    return bool(re.search(r"[\u0900-\u097F]", text or ""))


def clean_roman_word(word):
    """
    Removes final implicit schwa marker and converts remaining markers to 'a'.
    Example:
    नबिन -> nəbinə -> nabin
    राम -> ramə -> ram
    रिता -> rita -> rita
    """
    word = word.strip()

    if word.endswith("ə"):
        word = word[:-1]

    word = word.replace("ə", "a")

    return word


def romanize_nepali_name(name):
    name = str(name or "").strip()

    if not name:
        return ""

    # If already English, just title-case it.
    if not is_devanagari(name):
        return " ".join(part.capitalize() for part in name.split())

    result = []
    chars = list(name)

    for i, ch in enumerate(chars):
        next_ch = chars[i + 1] if i + 1 < len(chars) else ""

        if ch in CONSONANTS:
            base = CONSONANTS[ch]

            if next_ch in MATRAS:
                result.append(base)
            elif next_ch == VIRAMA:
                result.append(base)
            else:
                # implicit Nepali/Hindi schwa marker
                result.append(base + "ə")

        elif ch in MATRAS:
            result.append(MATRAS[ch])

        elif ch == VIRAMA:
            continue

        elif ch in VOWELS:
            result.append(VOWELS[ch])

        elif ch in ANUSVARA:
            result.append(ANUSVARA[ch])

        elif ch.isspace():
            result.append(" ")

        else:
            # Keep punctuation or unknown symbols as-is
            result.append(ch)

    raw = "".join(result)

    words = []
    for word in raw.split():
        cleaned = clean_roman_word(word)
        if cleaned:
            words.append(cleaned.capitalize())

    return " ".join(words)