from typing import Tuple
import math

from django.core.management.base import BaseCommand
from django.conf import settings
from es.client import client_from_config

# see https://www.elastic.co/docs/deploy-manage/production-guidance/optimize-performance/size-shards
SHARD_STORAGE_RANGE = (10e9, 50e9)
SHARD_DOCS_RANGE = (1, 200e6)

class Command(BaseCommand):
    help = '''
    Suggests optimal shard count based on existing index.

    Note: the shard count of an Elasticsearch indes can only be set at creation. This
    command can be used to evaluate the shard count and determine the optimal count for a
    new version.

    (Tip: you can also use this command after indexing a data sample.)
    '''

    def add_arguments(self, parser):
        parser.add_argument(
            'index',
            help='''Name of the index or alias''',
        )
        parser.add_argument(
            '--server',
            default='default',
            help='''Name of the Elasticsearch server (used in Django settings)''',
        )
        parser.add_argument(
            '--multiply-source', '-m',
            type=float,
            default=1.0,
            metavar='FACTOR',
            help='''If the target index will contain more source data, provide the
                estimated multiplication factor for the expansion. E.g. "2" indicates the
                source data will be doubled.''',
        )
        parser.add_argument(
            '--add-ner',
            action='store_true',
            help='''Whether the target index will add named entity annotations'''
        )
        parser.add_argument(
            '--add-bow',
            action='store_true',
            help='''Whether the target index will add bag-of-words data'''
        )


    def handle(
        self,
        index: str,
        server: str,
        add_ner: bool = False,
        add_bow: bool = False,
        multiply_source: float = 1.0,
        **kwargs,
    ):
        # get current storage
        storage, docs = self.fetch_stats(index, server)

        # estimate data expansion
        expected_docs = int(docs * multiply_source)
        if multiply_source != 1:
            print('Expected documents:', expected_docs)

        expansion_factor = self.check_expansion(add_ner, add_bow, multiply_source)
        expected_storage = storage * expansion_factor
        if expansion_factor != 1:
            print('Expected size in gigabytes:', self.format_size(expected_storage))

        # calculate optimal shard range
        suggest_min_storage, suggest_max_storage= self.calculate_shard_range(
            expected_storage, *SHARD_STORAGE_RANGE,
        )
        suggest_min_docs, suggest_max_docs = self.calculate_shard_range(
            expected_docs, *SHARD_DOCS_RANGE,
        )
        suggest_min = max(suggest_min_storage, suggest_min_docs)
        suggest_max = min(suggest_max_storage, suggest_max_docs)

        if suggest_min < suggest_max:
            print('Recommend between', suggest_min, 'and', suggest_max, 'shards')
        if suggest_min == suggest_max:
            print(f'Recommend', suggest_min, 'shard(s)')
        if suggest_min > suggest_max:
            print('Cannot generate recommendation: conflicting ranges based on storage and document count')


    def fetch_stats(self, index: str, server: str):
        server_config = settings.SERVERS.get(server)
        client = client_from_config(server_config)
        response = client.indices.stats(
            index=index,
            metric=['docs', 'shard_stats', 'store'],
        )

        total_storage = 0
        total_docs = 0

        if not len(response.body.get('indices')):
            raise Exception('No matching index found')

        print('CURRENT STATS:')

        for index, index_data in response.body['indices'].items():
            print('Index:', index)
            docs = index_data['primaries']['docs']['count']
            print('Documents:', docs)
            storage = index_data['primaries']['store']['size_in_bytes']
            print('Size in gigabytes:', self.format_size(storage))
            shards = index_data['primaries']['shard_stats']['total_count']
            print('Shards:', shards)
            print()

            total_storage += storage
            total_docs += docs

        if len(response.body['indices']) > 1:
            print('Total documents:', total_docs)
            print('Total size in gigabytes:', self.format_size(total_storage))
            print()

        return total_storage, total_docs


    def check_expansion(
        self,
        add_named_entities: bool,
        add_bag_of_words: bool,
        multiply_source: float,
    ) -> float:

        enrichment_factor = 1.0
        if add_named_entities:
            enrichment_factor  += 0.2
        if add_bag_of_words:
            enrichment_factor += 0.3

        return enrichment_factor * multiply_source


    def calculate_shard_range(
        self,
        value: int | float,
        min_value_per_shard: int | float,
        max_value_per_shard: int | float,
    ) -> Tuple[int, int]:
        max_count = math.ceil(value / min_value_per_shard)
        min_count = max(1, math.floor(value / max_value_per_shard))
        return min_count, max_count


    def format_size(self, bytes: int | float) -> str:
        return str(bytes * 1e-9) + ' GB'
