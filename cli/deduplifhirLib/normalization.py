"""
Module of functions that help to normalize fields of parsed patient data.
"""
import re



def remove_punctuation(text):
    """
    Removes punctuation from the given string.

    Arguments:
        text: the text to remove the punctuation from
    

    Returns:
        The input string without punctuation
    """
    symbols_to_remove = ".?!;:\'\""
    text_copy = text

    for symbol in symbols_to_remove:
        text_copy = text_copy.replace(symbol,'')
    return text_copy
