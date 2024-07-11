"""
Module of functions that help to normalize fields of parsed patient data.
"""
import re

abbreviations = {
    'USA': 'United States',
    'GB': 'Great Britain',
    'St.': 'Street',
    'Ave.': 'Avenue',
    'Blvd.': 'Boulevard',
    'Rd.': 'Road',
    'Dr.': 'Drive',
    'Ln.': 'Lane',
    'Ct.': 'Court',
    'Pl.': 'Place',
    'Sq.': 'Square',
    'Pkwy.': 'Parkway',
    'Cir.': 'Circle',
    'Terr.': 'Terrace',
    'Hwy.': 'Highway',
    'Mt.': 'Mount',
    'Ft.': 'Fort',
    'Pk.': 'Park',
    'Apt.': 'Apartment',
    'Bldg.': 'Building',
    'Fl.': 'Floor',
    'Ste.': 'Suite',
    'Rte.': 'Route',
    'N.': 'North',
    'S.': 'South',
    'E.': 'East',
    'W.': 'West',
    'NE.': 'Northeast',
    'NW.': 'Northwest',
    'SE.': 'Southeast',
    'SW.': 'Southwest',
    'Co.': 'County',
    'Jct.': 'Junction',
    'P.O.': 'Post Office',
    'dept.': 'department',
    'bldg.': 'building',
    'rm.': 'room',
    'ltd.': 'limited',
    'co.': 'company',
    'corp.': 'corporation',
    'inc.': 'incorporated',
    'intl.': 'international',
    'u.k.': 'United Kingdom',
    'u.s.': 'United States',
    'apt.': 'apartment',
    'ph.': 'phone',
    'fax.': 'fax',
    'mgr.': 'manager',
    'asst.': 'assistant',
    'dept.': 'department',
    'assoc.': 'association',
    'edu.': 'education',
    'univ.': 'university',
    'inst.': 'institute',
    'natl.': 'national',
    'am.': 'american',
    'eur.': 'european',
    'intl.': 'international',
    'org.': 'organization',
    'conf.': 'conference',
    'symp.': 'symposium'
}





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


def british_to_american(text):
    # Convert British "-our" endings to American "-or" endings
    text = re.sub(r'(\b\w+?)our\b', r'\1or', text)
    # Convert British "-ise" endings to American "-ize" endings
    text = re.sub(r'(\b\w+?)ise\b', r'\1ize', text)
    # Convert British "-yse" endings to American "-yze" endings
    text = re.sub(r'(\b\w+?)yse\b', r'\1yze', text)
    # Convert British "-ce" endings to American "-se" endings (e.g., defence to defense)
    text = re.sub(r'(\b\w+?)ce\b', r'\1se', text)
    # Convert British "-ogue" endings to American "-og" endings (e.g., catalogue to catalog)
    text = re.sub(r'(\b\w+?)ogue\b', r'\1og', text)
    # Convert British "centre" to American "center"
    text = re.sub(r'\bcentre\b', 'center', text)
    return text


if __name__ == "__main__":

    # Example usage
    text = "The rumour about the tumour was unfounded. He had to realise that the catalogue was necessary for the defence at the centre."
    normalized_text = british_to_american(text)
    print(normalized_text)  
    # Output: The rumor about the tumor was unfounded. He had to realize that the catalog was necessary for the defense at the center.
    # Example usage
    text = "The address is 123 St. James Ave., Apt. 4B, New York, NY, USA."
    for abbr, full in abbreviations.items():
        text = re.sub(r'\b' + re.escape(abbr) + r'\b', full, text)

    print(text)
    # Output: The address is 123 Street James Avenue, Apartment 4B, New York, NY, United States.

