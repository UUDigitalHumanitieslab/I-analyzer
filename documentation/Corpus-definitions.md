# Corpus definitions

Corpus definitions are the way that we configure each corpus in I-analyzer.

This documents gives a basic explanation of how corpus definitions "work" in the backend. For a more elaborate description of how to add corpus definition and what properties they contain, see [How to add a new corpus to I-analyzer](/documentation/How-to-add-a-new-corpus-to-Ianalyzer.md).

## Definition

At the moment, I-analyzer supports one method to define a corpus: by writing a custom Python class and including it in the backend.

We plan to support adding corpora through the interface; as we're working on this, some modules may suggest this possibility.

### Python class

Python-based corpora are written as Python classes. Each definition is a subclass of `CorpusDefinition`.

All corpus classes are contained in the [corpora](/backend/corpora/) directory (though it is technically possible to include definitions from elsewhere in the file system). This directory is not a Django app, but just a collection of scripts and metadata.

To be loaded into the application, the definition needs to be added to Django settings. The project includes a `CORPORA` setting which defines a mapping of names and python files, and lists which definitions should be loaded.

On startup, all configured python classes will be loaded into the database. During much of the runtime, the backend will refer to the database model rather than the python class. However, the python class is imported for more advanced features like document scans and word models. It is also used during indexing.

## Database models

Python definitions can be loaded into the database with the `loadcorpora` command in the backend. Normally, this is run when you start the server.

This command will parse any configured python corpora and save a `Corpus` and `CorpusConfiguration` object for them. If the python corpus cannot be loaded, the `Corpus` object will still exist in the database, it will be inactive.

### Corpus vs. CorpusConfiguration

The `CorpusConfiguration` model (and its related model `Field`) contains anything coming from the corpus definition class. It has a one-to-one relationship with `Corpus`.

The primary distinction is that `CorpusConfiguration` does not need to be preserved when you import corpus definitions: this model should be completely determined by the definition file, so it is overwritten each time.

`Corpus` is intended as a stable object that will be preserved when loading corpus definitions. This allows it to function as a reference point for search history, permissions, et cetera.

### The django admin

The Django admin interface is enabled for `CorpusConfiguration` and `Field`, mostly for the sake of providing an overview to developers. While it is possible to adjust settings here, they will be overwritten the next time you import corpus definitions.

### Hiding and deleting corpora

If you want to remove a corpus from your environment, remove it from the Django settings.

Removing a corpus from the settings will not delete the `Corpus` object. It has the following effect:

- The properties `corpus.active` and `corpus.has_python_definition` are set to `False`.
- The methods `corpus.ready_to_index()` and `corpus.read_to_publish()` will return `False`.
- The corpus will be hidden from the API and interface
- The python definition will no longer be imported during startup

Since the underlying `Corpus` is not actually deleted, related search history, downloads, tags, and permissions will be preserved. If you reinstate the corpus in settings, all of these will function as before.

At this point, you can also remove the `Corpus` object completely, which will remove all related data.

Note: if you want to temporarily hide a corpus in a production environment, it may be easier to adjust permissions in the Django admin, rather than adjust settings.
