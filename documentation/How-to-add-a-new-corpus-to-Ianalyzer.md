# How to add a new corpus to I-analzyer

The steps of adding a new corpus are usually the following:

- Create a new python class in the I-analyzer repository, which will describe the corpus
- Include the corpus in your local django settings and include (local) source data
- Load the corpus into your local database
- Create and populate a local elasticsearch index for the corpus
- Workshop the corpus definition, add unit tests
- Make a pull request
- Create and populate a production elasticsearch index on the test server (using your test branch)
- Include the corpus definition in the next release and deploy it in production
- Verify everything works as expected and adjust the corpus permissions in the production admin interface, so users can see it.

## Corpus definition
Adding a new corpus starts by adding a new corpus description `corpusname.py` to the `backend/corpora` directory. The corpus description imports global variables from `backend/ianalyzer/settings.py`. The definition file should be listed under `CORPORA` in the settings. In a development environment, this should happen in `backend/ianalyzer/settings_local.py`. More on the use of settings below.

The corpus definition is a python class definition, subclassing the `CorpusDefinition` class (found in `addcorpus/corpus.py`). You will normally use a datatype-specific subclass of `CorpusDefinition`, like this:

```python
from addcorpus.corpus import CSVCorpusDefinition

class MyCorpus(CSVCorpusDefinition):
    pass
```

The `CorpusDefinition` classes inherit functionality from the package `ianalyzer_readers`, which defines more general `Reader` classes to read data from source files.

This provides the basis for an I-analyzer corpus that will define how to read the source data, index it to elasticsearch, and present a search interface in the frontend. However, most properties still need to be filled in.

The corpus class should define the following properties:

- `title`: Title to be used in the interface.
- `description`: Short description, appears as a subtitle in the interface.
- `data_directory`: Path to the source files. Always get this from the setttings.
- `min_date`, `max_date`: The minimum and maximum dates for documents.
- `es_index`: the name of the index in elasticsearch.
- `image`: a path or url to the image used for the corpus in the interface.
- `fields`: a list of `Field` objects. See [defining corpus fields](./Defining-corpus-fields.md).
- `languages`: a list of ISO 639 codes of the languages used in your corpus. Corpus languages are intended as a way for users to select interesting datasets, so only include languages for which your corpus contains a meaningful amount of data. The list should go from most to least frequent.
- `category`: the type of data in the corpus. The list of options is in `backend/addcorpus/constants`.

The following properties are optional:
- `es_alias`: an alias for the index in elasticsearch.
- `es_settings`: overwrites the `settings` property of the elasticsearch index. Can be generated using [es_settings.py](../backend/addcorpus/es_settings.py)
- `scan_image_type`: the filetype of scanned documents, if these are included.
- `allow_image_download`
- `desription_page`: filename of markdown document with a comprehensive description, located in a subdirectory `description` of the corpus definition directory.
- `document_context`: specifies fields that define the natural grouping of documents.
- `default_sort`: specifies the default method to sort search result.
- `language_field`: if your corpus contains documents in multiple language, you can specify the name of the field that stores the IETF tag for each document.

The corpus class should also define a function `sources(self, start, end)` which iterates source files (presumably within on `data_directory`). The `start` and `end` properties define a date range: if possible, only yield files within the range. Each source file should be tuple of a filename and a dict with metadata.

### Different types of readers

The `CorpusDefinition` class is a subclass of the `Reader` in `ianalyzer_readers`. `Reader` is a base class that does not provide much for data extraction.

Most corpus definitions also inherit from a more specific `Reader` that provides functionality for the type of source data, e.g. `XMLReader`, `CSVReader`, etc. For convenience, you can use the classes `XMLCorpusDefinition`, `CSVCorpusDefinition`, etc., defined in [corpus.py](/backend/addcorpus/python_corpora/corpus.py).

See [the documentation of ianalyzer_readers](https://ianalyzer-readers.readthedocs.io/en/latest/) for the available `Reader` classes and the API for each of them.

## Settings file

The django settings can be used to configure variables that may be depend on the environment. Please use the following naming convention.

```python
CORPUSNAME_DATA = '/MyData/CorpusData' # the directory where the xml / html or other files are located
CORPUSNAME_ES_INDEX = 'dutchbanking' # the name that elasticsearch gives to the index
CORPUSNAME_SCAN_IMAGE_TYPE = 'image/png' #mimetype of document media
```

These can be retrieved in the corpus definition, for example:

```python
from django.conf import settings

class Times(XMLCorpus):
    title = "Times"
    description = "Newspaper archive, 1785-2010"
    min_date = datetime(year=1785, month=1, day=1)
    max_date = datetime(year=2010, month=12, day=31)
    data_directory = settings.TIMES_DATA
    es_index = getattr(settings, 'TIMES_ES_INDEX', 'times')
    ...
```

Note that for a property like the elasticsearch index, we define a default value but make it possible to override this in the settings file.

### Corpus selection

The dictionary `CORPORA` defines the name of the corpora and their filepath. It is defined as

```python
CORPORA = {
    'times': '.../times.py',
}
```

The key of the corpus must match the name of the corpus class (but lowercase/hyphenated), so `'times'` is the key for the `Times` class. Typically, the key also matches the `es_index` of the corpus, as well as its filename.

`CORPUS_SERVER_NAMES` defines to which server (defined in `SERVERS`) the backend should make requests. You only need to include corpora that do not use the `'default'` server.

```python
CORPUS_SERVER_NAMES = {
    'times': 'special_server',
}
```

### settings vs. settings_local
`settings.py` imports all information in `settings_local.py`. If a variable is defined in both, `settings_local` overrules `settings`. All sensitive information (server names, user names, passwords) should be in `settings_local.py`, as this will 1) never be committed to github, and 2) be located in the `private` folder upon deployment.

## Elasticsearch
Once the corpus definition and associated settings are added, the only remaining step is to make the Elasticsearch index. By running `yarn django index corpusname`, information is extracted and sent to Elasticsearch.
Optional flags:
- `-s 1990-01-01` sets different start date for indexing
- `-e 2000-12-31` sets different end data for indexing
- `-d` specifies that an existing index of the same name should be deleted first (if not specified, defaults to false, meaning that extra data can be added while existing data is not overwritten)

The start and end date flags are passed on the `sources` function of the corpus (see above). If you did not utilise them there, they will not do anything.

## Validation

The `CorpusDefinition` class has no built-in validation. However, once you start using the corpus, many of the properties defined in the python class will be loaded into the `CorpusConfiguration` database model. This step does include some validation, so it may raise errors. You can run the import script with `yarn django loadcorpora`. It is also run when you start a development server with `yarn start-back`.

## Unit testing

It is strongly recommended that you include unit tests for your corpus. A minimal test is to try to load your corpus into the database. In addition, it is recommended that you include some tests that check the output of the data extraction.

The rechtspraak corpus includes good examples of such tests.
