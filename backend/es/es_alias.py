#!/usr/bin/env python3
import re

from addcorpus.models import Corpus, CorpusConfiguration
from ianalyzer.elasticsearch import elasticsearch

import logging
logger = logging.getLogger('indexing')


def alias(corpus: Corpus, clean=False):
    '''
    Script to create, update and remove aliases from ES
    '''
    corpus_config = corpus.configuration
    corpus_name = corpus.name
    index_name = corpus_config.es_index
    index_alias = corpus_config.es_alias
    client = elasticsearch(corpus_name)

    alias = index_alias if index_alias else index_name
    indices = client.indices.get(index='{}-*'.format(index_name))
    highest_version = get_highest_version_number(indices, alias)

    actions = []

    for index_name, properties in indices.items():
        is_aliased = alias in properties['aliases'].keys()
        is_highest_version = extract_version(index_name, alias) == highest_version

        if not is_highest_version and clean:
            logger.info('Removing index `{}`'.format(index_name))
            # note that removing an index automatically removes alias
            actions.append({'remove_index': {'index': index_name}})

        if not is_highest_version and is_aliased and not clean:
            logger.info('Removing alias `{}` for index `{}`'.format(alias, index_name))
            actions.append(
                {'remove': {'index': index_name, 'alias': alias}})

        if is_highest_version and not is_aliased:
            logger.info('Adding alias `{}` for index `{}`'.format(alias, index_name))
            actions.append(
                {'add': {'index': index_name, 'alias': alias}})
        elif is_highest_version and is_aliased:
            logger.info('Alias `{}` already exists for `{}`, skipping alias creation'.format(
                alias, index_name))

    if len(actions) > 0:
        client.indices.update_aliases(actions=actions)
    logger.info('Done updating aliases')


def get_current_index_name(corpus: CorpusConfiguration, client) -> str:
    """get the name of the current corpus' associated index"""
    alias = corpus.es_alias or corpus.es_index
    indices = client.indices.get(index="{}".format(alias))
    return max(sorted(indices.keys()))


def get_new_version_number(client, alias, current_index=None):
    '''
    Get version number for a new versioned index (e.g. `indexname-1`).
    Will be 1 if an index with name `alias` exists,
    or neither an index nor an alias with name `alias` exists.
    If an alias exists, the version number of the existing index with
    the latest version number will be used to determine the new version
    number. Note that the latter relies on the existence of version numbers in
    the index names (e.g. `indexname-1`).

    Parameters
        client -- ES client
        alias -- The alias any versioned indices might be under.
        current_index -- The `es_index` (i.e. unversioned name) currently being updated.
            This will be used to exclude indices starting with different names under the same alias.
    '''
    if not client.indices.exists(index=alias):
        return 1
    # get the indices aliased with `alias`
    indices = client.indices.get_alias(name=alias)
    highest_version = get_highest_version_number(indices, current_index)
    return str(highest_version + 1)

def extract_version(index_name, current_index):
    '''
    Helper function to extract version number from an index name, given an alias.
    Format of the index_name should be `index_name-<version>`, e.g., `index_name-5,
    while `index_name-something-else-5` will not be detected as a version.
    Returns None if no version number is found.
    '''
    match = re.match('{}-([0-9]+)$'.format(current_index), index_name)
    if match:
        return int(match.group(1))

def get_highest_version_number(indices, current_index=None):
    '''
    Get the version number of the index with the highest version number currently present in ES.
    Note that this relies on the existence of version numbers in the index names (e.g. `index_name-1`).

    Parameters:
        indices -- a dict with the ES response (not a list of names!)
        current_index -- The `es_index` (i.e. unversioned) currently being updated.
            This will be used to exclude indices starting with different names under the same alias.
    '''
    if type(indices) is list:
        raise RuntimeError('`indices` should not be list')
    versions = [extract_version(index_name, current_index) for index_name in indices.keys()]
    try:
        return max([v for v in versions if v is not None])
    except:
        return 0
