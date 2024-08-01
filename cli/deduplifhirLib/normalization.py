"""
Module of functions that help to normalize fields of parsed patient data.
"""
import re
from dateutil import parser as date_parser
from dateutil.parser import ParserError
from text_to_num import alpha2digit

NAME_ABBREVIATION_SYMBOLS = {
    ' jr ': 'junior',
    ' sr ': 'senior',
    ' dr ': 'doctor',
    ' mr ': 'mister',
    ' mrs ': 'miss',
    ' ms ': 'miss',
    ' prof ': 'professor',
    ' rev ': 'reverend',
    ' hon ': 'honorable',
    ' st ': 'saint',
    ' capt ': 'captain',
    ' lt ': 'lieutenant',
    ' col ': 'colonel',
    ' gen ': 'general',
    ' maj ': 'major',
    ' sgt ': 'sergeant',
    ' cpl ': 'corporal',
    ' adm ': 'admiral',
    ' cmdr ': 'commander',
    ' ens ': 'ensign',
    ' pvt ': 'private',
    ' fr ': 'father',
    ' br ': 'brother',
    ' dcn ': 'deacon',
    ' ven ': 'venerable',
    ' min ': 'minister',
    ' pres ': 'president',
    ' gov ': 'governor',
    ' sen ': 'senator',
    ' rep ': 'representative',
    ' amb ': 'ambassador',
    ' sec ': 'secretary',
    ' chmn ': 'chairman',
    ' exec ': 'executive',
    ' mgr ': 'manager',
    ' dir ': 'director',
    ' asst ': 'assistant',
    ' vp ': 'vice president',
    ' ceo ': 'chief executive officer',
    ' coo ': 'chief operating officer',
    ' cto ': 'chief technology officer',
    ' cfo ': 'chief financial officer'
}

PLACE_ABBREVIATION_SYMBOLS = {
    ' st ' : 'st',
    ' usa ': 'united states',
    ' gb ': 'great britain',
    ' street ': 'st',
    ' saint ': 'st',
    ' ave ': 'avenue',
    ' blvd ': 'boulevard',
    ' rd ': 'road',
    ' dr ': 'drive',
    ' ln ': 'lane',
    ' pl ': 'place',
    ' sq ': 'square',
    ' pkwy ': 'parkway',
    ' cir ': 'circle',
    ' terr ': 'terrace',
    ' hwy ': 'highway',
    ' ft ': 'fort',
    ' pk ': 'park',
    ' apt ': 'apartment',
    ' floor ': 'fl',
    ' ste ': 'suite',
    ' rte ': 'route',
    ' n ': 'north',
    ' s ': 'south',
    ' e ': 'east',
    ' w ': 'west',
    ' nw ': 'northwest',
    ' se ': 'southeast',
    ' sw ': 'southwest',
    ' jct ': 'junction',
    ' po ': 'post office',
    ' bldg ': 'building',
    ' rm ': 'room',
    ' ltd ': 'limited',
    ' corp ': 'corporation',
    ' inc ': 'incorporated',
    ' intl ': 'international',
    ' uk ': 'united kingdom',
    ' us ': 'united states',
    ' ph ': 'phone',
    ' fax ': 'fax',
    ' mgr ': 'manager',
    ' asst ': 'assistant',
    ' dept ': 'department',
    ' assoc ': 'association',
    ' edu ': 'education',
    ' univ ': 'university',
    ' inst ': 'institute',
    ' natl ': 'national',
    ' am ': 'american',
    ' eur ': 'european',
    ' org ': 'organization',
    ' conf ': 'conference',
    ' symp ': 'symposium',
    ' al ': 'alabama',
    ' ak ': 'alaska',
    ' az ': 'arizona',
    ' ar ': 'arkansas',
    ' ca ': 'california',
    ' co ': 'colorado',
    ' ct ': 'connecticut',
    ' de ': 'delaware',
    ' fl ': 'florida',
    ' ga ': 'georgia',
    ' hi ': 'hawaii',
    ' id ': 'idaho',
    ' il ': 'illinois',
    ' in ': 'indiana',
    ' ia ': 'iowa',
    ' ks ': 'kansas',
    ' ky ': 'kentucky',
    ' la ': 'louisiana',
    ' me ': 'maine',
    ' md ': 'maryland',
    ' ma ': 'massachusetts',
    ' mi ': 'michigan',
    ' mn ': 'minnesota',
    ' ms ': 'mississippi',
    ' mo ': 'missouri',
    ' mt ': 'montana',
    ' ne ': 'nebraska',
    ' nv ': 'nevada',
    ' nh ': 'new hampshire',
    ' nj ': 'new jersey',
    ' nm ': 'new mexico',
    ' ny ': 'new york',
    ' nc ': 'north carolina',
    ' nd ': 'north dakota',
    ' oh ': 'ohio',
    ' ok ': 'oklahoma',
    ' or ': 'oregon',
    ' pa ': 'pennsylvania',
    ' ri ': 'rhode island',
    ' sc ': 'south carolina',
    ' sd ': 'south dakota',
    ' tn ': 'tennessee',
    ' tx ': 'texas',
    ' ut ': 'utah',
    ' vt ': 'vermont',
    ' va ': 'virginia',
    ' wa ': 'washington',
    ' wv ': 'west virginia',
    ' wi ': 'wisconsin',
    ' wy ': 'wyoming'
}


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
    PLACE_ABBREVIATION_SYMBOLS
)

REPLACE_PROPER_NAME_SYMBOLS_PATTERN = compile_abbreviation_map_regex(
    NAME_ABBREVIATION_SYMBOLS
)


def replace_abbreviations(
    input_text,
    pattern=REPLACE_PLACE_NAME_SYMBOLS_PATTERN,
    symbols=PLACE_ABBREVIATION_SYMBOLS
    ):
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


def remove_non_alphanum(input_text):
    """
    Removes punctuation from the given string.

    Arguments:
        input_text: the input_text to remove the punctuation from
    

    Returns:
        The input string without punctuation
    """
    #symbols_to_remove = ".,?!;:\'\""

    return re.sub(r'[^a-zA-Z0-9 ]', '', input_text.replace(',', ' '))

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


def normalize_date_text(input_text):
    """
    Normalizes the given date string

    Arguments:
        input_text: the input date text to normalize
    
    Returns:
        The normalized date string
    """
    try:
        d = date_parser.parse(input_text)
    except ParserError as e:
        print(f"Error when trying to parse date {input_text}")
        print(f"Error: {e}")
        return input_text
    except OverflowError as e:
        print("Overflow error when trying to parse date!")
        print("Input string too long!")
        print(f"Error: {e}")
        return input_text
    return d.strftime("%Y-%m-%d")

def normalize_name_text(input_text):
    """
    Normalizes the given name string

    Arguments:
        input_text: the input_text to normalize
    

    Returns:
        The normalized string
    """
    text_copy = input_text
    #text_copy = british_to_american(text_copy) Not needed
    #Replace abbreviations that occur in place names
    text_copy = remove_non_alphanum(text_copy)
    text_copy = replace_abbreviations(
        text_copy.lower(),
        pattern=REPLACE_PROPER_NAME_SYMBOLS_PATTERN,
        symbols=NAME_ABBREVIATION_SYMBOLS
        )
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
    #text_copy = british_to_american(text_copy) not needed
    try:
        text_copy = alpha2digit(text_copy,"en")
    except ValueError:
        ...
    text_copy = remove_non_alphanum(text_copy)
    print(text_copy)
    text_copy = replace_abbreviations(text_copy.lower())

    return text_copy.lower()

if __name__ == "__main__":

    NAME_TEXT = "Greene,Jacquleine"
    print(normalize_name_text(NAME_TEXT))

    PLACE_TEXT = "7805 Kartina Motorawy Apt. three hundred thirteen ,Taylorstad,New Hampshire"

    print(normalize_addr_text(PLACE_TEXT))

    DATE_TEXT = "December 10, 1999"
    print(normalize_date_text(DATE_TEXT))

    NUM_TEXT = "I have one hundred twenty three apples and forty-five oranges. Valetnine"
    print(alpha2digit(NUM_TEXT,'en'))
