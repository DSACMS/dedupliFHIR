"""
Module of functions that help to normalize fields of parsed patient data.
"""
import re

NAME_ABBREVIATION_SYMBOLS = {
    ' Jr. ': 'Junior',
    ' Sr. ': 'Senior',
    ' Dr. ': 'Doctor',
    ' Mr. ': 'Mister',
    ' Mrs. ': 'Miss',
    ' Ms. ': 'Miss',
    ' Prof. ': 'Professor',
    ' Rev. ': 'Reverend',
    ' Hon. ': 'Honorable',
    ' St. ': 'Saint',
    ' Capt. ': 'Captain',
    ' Lt. ': 'Lieutenant',
    ' Col. ': 'Colonel',
    ' Gen. ': 'General',
    ' Maj. ': 'Major',
    ' Sgt. ': 'Sergeant',
    ' Cpl. ': 'Corporal',
    ' Adm. ': 'Admiral',
    ' Cmdr. ': 'Commander',
    ' Ens. ': 'Ensign',
    ' Pvt. ': 'Private',
    ' Fr. ': 'Father',
    ' Br. ': 'Brother',
    ' Dcn. ': 'Deacon',
    ' Ven. ': 'Venerable',
    ' Min. ': 'Minister',
    ' Pres. ': 'President',
    ' Gov. ': 'Governor',
    ' Sen. ': 'Senator',
    ' Rep. ': 'Representative',
    ' Amb. ': 'Ambassador',
    ' Sec. ': 'Secretary',
    ' Chmn. ': 'Chairman',
    ' Exec. ': 'Executive',
    ' Mgr. ': 'Manager',
    ' Dir. ': 'Director',
    ' Asst. ': 'Assistant',
    ' VP ': 'Vice President',
    ' CEO ': 'Chief Executive Officer',
    ' COO ': 'Chief Operating Officer',
    ' CTO ': 'Chief Technology Officer',
    ' CFO ': 'Chief Financial Officer'
}

PLACE_ABBREVIATION_SYMBOLS = {
    ' St ' : 'St.',
    ' USA ': 'United States',
    ' GB ': 'Great Britain',
    ' Street ': 'St.',
    ' Saint ': 'St.',
    ' Ave. ': 'Avenue',
    ' Blvd. ': 'Boulevard',
    ' Rd. ': 'Road',
    ' Dr. ': 'Drive',
    ' Ln. ': 'Lane',
    ' Ct. ': 'Court',
    ' Pl. ': 'Place',
    ' Sq. ': 'Square',
    ' Pkwy. ': 'Parkway',
    ' Cir. ': 'Circle',
    ' Terr. ': 'Terrace',
    ' Hwy. ': 'Highway',
    ' Mt. ': 'Mount',
    ' Ft. ': 'Fort',
    ' Pk. ': 'Park',
    ' Apt. ': 'Apartment',
    ' Bldg. ': 'Building',
    ' Fl. ': 'Floor',
    ' Ste. ': 'Suite',
    ' Rte. ': 'Route',
    ' N. ': 'North',
    ' S. ': 'South',
    ' E. ': 'East',
    ' W. ': 'West',
    ' NE. ': 'Northeast',
    ' NW. ': 'Northwest',
    ' SE. ': 'Southeast',
    ' SW. ': 'Southwest',
    ' Co. ': 'County',
    ' Jct. ': 'Junction',
    ' P.O. ': 'Post Office',
    ' dept. ': 'department',
    ' bldg. ': 'building',
    ' rm. ': 'room',
    ' ltd. ': 'limited',
    ' co. ': 'company',
    ' corp. ': 'corporation',
    ' inc. ': 'incorporated',
    ' intl. ': 'international',
    ' u.k. ': 'United Kingdom',
    ' u.s. ': 'United States',
    ' apt. ': 'apartment',
    ' ph. ': 'phone',
    ' fax. ': 'fax',
    ' mgr. ': 'manager',
    ' asst. ': 'assistant',
    ' dept ': 'department',
    ' assoc. ': 'association',
    ' edu. ': 'education',
    ' univ. ': 'university',
    ' inst. ': 'institute',
    ' natl. ': 'national',
    ' am. ': 'american',
    ' eur. ': 'european',
    ' intl ': 'international',
    ' org. ': 'organization',
    ' conf. ': 'conference',
    ' symp. ': 'symposium',
    ' AL ': 'Alabama',
    ' AK ': 'Alaska',
    ' AZ ': 'Arizona',
    ' AR ': 'Arkansas',
    ' CA ': 'California',
    ' CO ': 'Colorado',
    ' CT ': 'Connecticut',
    ' DE ': 'Delaware',
    ' FL ': 'Florida',
    ' GA ': 'Georgia',
    ' HI ': 'Hawaii',
    ' ID ': 'Idaho',
    ' IL ': 'Illinois',
    ' IN ': 'Indiana',
    ' IA ': 'Iowa',
    ' KS ': 'Kansas',
    ' KY ': 'Kentucky',
    ' LA ': 'Louisiana',
    ' ME ': 'Maine',
    ' MD ': 'Maryland',
    ' MA ': 'Massachusetts',
    ' MI ': 'Michigan',
    ' MN ': 'Minnesota',
    ' MS ': 'Mississippi',
    ' MO ': 'Missouri',
    ' MT ': 'Montana',
    ' NE ': 'Nebraska',
    ' NV ': 'Nevada',
    ' NH ': 'New Hampshire',
    ' NJ ': 'New Jersey',
    ' NM ': 'New Mexico',
    ' NY ': 'New York',
    ' NC ': 'North Carolina',
    ' ND ': 'North Dakota',
    ' OH ': 'Ohio',
    ' OK ': 'Oklahoma',
    ' OR ': 'Oregon',
    ' PA ': 'Pennsylvania',
    ' RI ': 'Rhode Island',
    ' SC ': 'South Carolina',
    ' SD ': 'South Dakota',
    ' TN ': 'Tennessee',
    ' TX ': 'Texas',
    ' UT ': 'Utah',
    ' VT ': 'Vermont',
    ' VA ': 'Virginia',
    ' WA ': 'Washington',
    ' WV ': 'West Virginia',
    ' WI ': 'Wisconsin',
    ' WY ': 'Wyoming'
}

def add_permutations_to_dict_pattern(symbol_dict):
    """
    Add permutations of the keys from a dict and map them to the same value
    as the original key. 

    For example we make every key also match to its lowercase version,
    as well as mapping to the version with punctuation and proper spaces. 


    Arguments:
        symbol_dict: dictionary of symbols to add permutations to 
    
    Returns:
        Expanded version of dict input
    """
    #Add some permutations to the dictionary manually once
    abvs = list(symbol_dict.keys())
    for key in abvs:
        symbol_dict[key.lower()] = symbol_dict[key]
        symbol_dict[key[:-1] + ','] = symbol_dict[key]
        symbol_dict[key[:-1] + '.'] = symbol_dict[key]


        if key[-1] == '.':
            symbol_dict[key[:-2] + ' '] = symbol_dict[key]
            symbol_dict[key[:-2] + ', '] = symbol_dict[key]

    return symbol_dict


def compile_abbreviation_map_regex(symbol_dict):
    """
    Compile a regular expression that converts the dictionary pattern into a 
    regex that matches and replaces every instance of the keys found in the dict
    with their proper normalized values.


    Arguments:
        symbol_dict: dictionary of symbols to replace
    
    Returns:
        Regex pattern object.
    """

    # Create a regex REPLACE_PLACE_NAME_SYMBOLS_PATTERN that matches any of the
    #  keys in the abbreviation dictionary
    return re.compile('|'.join(re.escape(key) for key in symbol_dict.keys()))

REPLACE_PLACE_NAME_SYMBOLS_PATTERN = compile_abbreviation_map_regex(
    add_permutations_to_dict_pattern(
        PLACE_ABBREVIATION_SYMBOLS
    )
)

REPLACE_PROPER_NAME_SYMBOLS_PATTERN = compile_abbreviation_map_regex(
    add_permutations_to_dict_pattern(
        NAME_ABBREVIATION_SYMBOLS
    )
)


def replace_abbreviations(input_text,pattern=REPLACE_PLACE_NAME_SYMBOLS_PATTERN,symbols=PLACE_ABBREVIATION_SYMBOLS):
    """
    Normalizes common abbreviations with a pre-compiled regular expression.

    Arguments:
        input_text: the input_text to remove the abbreviations from.

    Returns:
        The input string without the abbreviations.
    """
    # Define a function to use as the replacement argument in re.sub
    def replacer(match):
        return " " + symbols[match.group(0)] + " "

    # Use re.sub with the REPLACE_PLACE_NAME_SYMBOLS_PATTERN
    #  and replacer function to replace abbreviations
    return pattern.sub(replacer, input_text)


def remove_punctuation(input_text):
    """
    Removes punctuation from the given string.

    Arguments:
        input_text: the input_text to remove the punctuation from
    

    Returns:
        The input string without punctuation
    """
    symbols_to_remove = ".,?!;:\'\""
    text_copy = input_text

    for symbol in symbols_to_remove:
        text_copy = text_copy.replace(symbol,'')
    return text_copy


def british_to_american(input_text):
    """
    Removes punctuation from the given string.

    Arguments:
        input_text: the input_text to replace british spellings of
    

    Returns:
        The input string without british spellings
    """
    # Convert British "-our" endings to American "-or" endings
    input_text = re.sub(r'(\b\w+?)our\b', r'\1or', input_text)
    # Convert British "-ise" endings to American "-ize" endings
    input_text = re.sub(r'(\b\w+?)ise\b', r'\1ize', input_text)
    # Convert British "-yse" endings to American "-yze" endings
    input_text = re.sub(r'(\b\w+?)yse\b', r'\1yze', input_text)
    # Convert British "-ce" endings to American "-se" endings (e.g., defence to defense)
    input_text = re.sub(r'(\b\w+?)ce\b', r'\1se', input_text)
    # Convert British "-ogue" endings to American "-og" endings (e.g., catalogue to catalog)
    input_text = re.sub(r'(\b\w+?)ogue\b', r'\1og', input_text)
    # Convert British "centre" to American "center"
    input_text = re.sub(r'\bcentre\b', 'center', input_text)
    return input_text


def normalize_name_text(input_text):
    """
    Normalizes the given name string

    Arguments:
        input_text: the input_text to normalize
    

    Returns:
        The normalized string
    """
    text_copy = input_text
    text_copy = british_to_american(text_copy)
    #Replace abbreviations that occur in place names
    text_copy = replace_abbreviations(
        text_copy,pattern=REPLACE_PROPER_NAME_SYMBOLS_PATTERN,symbols=NAME_ABBREVIATION_SYMBOLS
        )
    text_copy = remove_punctuation(text_copy)
    return text_copy.lower()

def normalize_addr_text(input_text):
    """
    Normalizes the given address string

    Arguments:
        input_text: the input_text to normalize
    

    Returns:
        The normalized string
    """
    text_copy = input_text
    text_copy = british_to_american(text_copy)
    text_copy = replace_abbreviations(text_copy)
    text_copy = remove_punctuation(text_copy)

    return text_copy.lower()

if __name__ == "__main__":

    NAME_TEXT = "Greene,Jacquleine"
    print(normalize_name_text(NAME_TEXT))

    PLACE_TEXT = "7805 Kartina Motorawy Apt. 313,Taylorstad,New Hampshire"

    print(normalize_addr_text(PLACE_TEXT))
