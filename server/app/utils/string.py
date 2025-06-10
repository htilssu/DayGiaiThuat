from unidecode import unidecode


def remove_vi_accents(text: str) -> str:
    """
    Remove vietnamese accents from a string.
    """
    return unidecode(text)
