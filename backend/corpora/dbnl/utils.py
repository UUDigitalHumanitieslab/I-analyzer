import re
from bs4 import BeautifulSoup
import os
from langcodes import standardize_tag, Language

from addcorpus.python_corpora.extract import Pass, Combined, CSV

# === METADATA EXTRACTION ===

def index_by_id(data):
    return {
        row['title_id']: row
        for row in data
    }

PERIODIAL_PREFIX = '[tijdschrift]'

def is_periodical(name):
    return name.startswith(PERIODIAL_PREFIX)

def sorted_and_unique(items):
    if items:
        return list(sorted(set(items)))

def get_periodical(names):
    periodicals = list(filter(is_periodical, names))
    format = lambda name: name[len(PERIODIAL_PREFIX):].strip()
    if periodicals:
        return ', '.join(sorted_and_unique(map(format, periodicals)))

def which_are_people(names):
    '''
    returns which names are NOT names of periodals
    '''
    return map(lambda name: name and not is_periodical(name), names)

def which_unique(items):
    '''
    Which items in a list should be included to ensure uniqueness

    returns a list of booleans the same length as items, where `result[n] == True`
    iff `items[n]` is the first occurrence of that value.
    '''

    is_first = lambda n: n == 0 or items[n] not in items[:n]
    return map(is_first, range(len(items)))

def filter_values_by(values, which):
    if not values:
        return None

    return [
        value
        for value, include in zip(values, which)
        if include
    ]

def filter_by(values_extractor, condition_extractor):
    '''
    Takes an extractor that returns a list of values and one that returns a list
    of booleans, of the same length.

    Extracts each value of the first extractor, where the corresponding value
    of the second extractor is truthy.
    '''

    return Combined(
        values_extractor, condition_extractor,
        transform=lambda data : filter_values_by(*data)
    )

def format_gender(value):
    '''
    Format gender into a string for clarity

    Gender is coded as a binary value (∈ ['1', '0']).
    0 is used for men, unknown/anonymous authors, and institutions,
    1 is used for women.
    '''

    return {'0': 'man/unknown', '1': 'woman'}.get(value, None)

def by_author(extractor):
    # extractor of which rows represent unique authors
    _which_are_authors = Combined(
        CSV(
            'pers_id',
            multiple=True,
            transform=which_unique,
        ),
        CSV(
            'achternaam',
            multiple=True,
            transform=which_are_people,
        ),
        transform=lambda values: map(all, zip(*values))
    )

    return Pass(
        filter_by(
            extractor,
            _which_are_authors,
        ),
        transform=join_values,
    )

# === METADATA-ONLY RECORDS ===

class BlankXML:
    def __init__(self, data_directory):
        self.filename = os.path.join(data_directory, '_.xml')

    def __enter__(self):
        # create an xml that will generate one "spoonful", i.e. one document
        # but no actual content
        soup = BeautifulSoup('<TEI.2><div type="chapter"></div></TEI.2>', 'lxml-xml')
        with open(self.filename, 'w') as file:
            file.write(soup.prettify())

        return self.filename

    def __exit__(self, exc_type, exc_value, traceback):
        os.remove(self.filename)

# === UTILITY FUNCTIONS ===

def join_values(values):
    '''
    Join extracted values into a string with proper handling of None values.

    Input should be an iterable of strings or None.

    - If all values are '', None, or '?', return None
    - If some values are non-empty, convert empty values to '?' and join
    them into a single string.
    '''

    if values:
        formatted = [value or '?' for value in values]
        if any(value != '?' for value in formatted):
            return ', '.join(formatted)

def between_years(year, start_date, end_date):
    if start_date and year < start_date.year:
        return False

    if end_date and year > end_date.year:
        return False

    return True

def format_name(parts):
    '''Format a person's name'''

    #exception for anonymous authors
    if parts[0] == 'anoniem':
        work = parts[-1]
        return f'anoniem [{work}]'

    return ' '.join(filter(None, parts))

LINE_TAG = re.compile('^(p|l|head|row|item)$')
'''
Describes the tags for a single line in the content. Can be:

- <p> paragraphs
- <head> headers
- <l> line (used for poems/songs)
- <row> table rows (used for poems/songs)
- <item> list items
'''

def append_to_tag(soup, tag, padding):
    '''
    Insert a string at the end of each instance of a tag.
    '''

    for tag in soup.find_all(tag):
        tag.append(padding)

    return soup

def pad_content(node):
    pad_cells = lambda n: append_to_tag(n, 'cell', ' ')
    pad_linebreaks = lambda n: append_to_tag(n, 'lb', '\n')
    pad_cells(pad_linebreaks(node))
    return [node]

def standardize_language_code(code):
    if code:
        return standardize_tag(code)

def single_language_code(code):
    if code and '-' in code:
        primary, *rest = code.split('-')
        return primary
    return code

def language_name(code):
    if not code:
        return None
    codes = code.split('-')
    names = set(map(
        lambda code: Language.make(language=standardize_tag(code)).display_name(),
        codes
    ))
    return ', '.join(names)
