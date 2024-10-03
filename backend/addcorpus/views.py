import os

from addcorpus.models import (Corpus, CorpusConfiguration, CorpusDataFile,
                              CorpusDocumentationPage)
from addcorpus.permissions import (CanSearchCorpus, IsCurator, IsCuratorOrReadOnly,
                                   corpus_name_from_request)
from addcorpus.python_corpora.load_corpus import (corpus_dir)
from addcorpus.serializers import (CorpusDataFileSerializer,
                                   CorpusDocumentationPageSerializer,
                                   CorpusJSONDefinitionSerializer,
                                   CorpusSerializer)
from addcorpus.utils import get_csv_info
from django.conf import settings
from django.http.response import FileResponse
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.permissions import (IsAuthenticated)
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView


class CorpusView(viewsets.ReadOnlyModelViewSet):
    '''
    List all available corpora
    '''

    serializer_class = CorpusSerializer

    def get_queryset(self):
        return self.request.user.searchable_corpora()


class CorpusDocumentationPageViewset(viewsets.ModelViewSet):
    '''
    Markdown documentation pages for corpora.
    '''

    permission_classes = [IsCuratorOrReadOnly]
    serializer_class = CorpusDocumentationPageSerializer

    def get_queryset(self):
        # curators are not limited to active corpora (to allow editing)
        if self.request.user.is_staff:
            corpora = Corpus.objects.all()
        else:
            corpora = self.request.user.searchable_corpora()

        queried_corpus = self.request.query_params.get('corpus')
        if queried_corpus:
            corpora = corpora.filter(name=queried_corpus)

        return CorpusDocumentationPage.objects.filter(
            corpus_configuration__corpus__in=corpora
        )


class CorpusImageView(APIView):
    '''
    Return the image for a corpus.
    '''

    permission_classes = [CanSearchCorpus, IsCuratorOrReadOnly]

    def get(self, request, *args, **kwargs):
        corpus_name = corpus_name_from_request(request)
        corpus_config = CorpusConfiguration.objects.get(corpus__name=corpus_name)
        if corpus_config.image:
            path = corpus_config.image.path
        else:
            path = settings.DEFAULT_CORPUS_IMAGE

        return FileResponse(open(path, 'rb'))


class CorpusDocumentView(APIView):
    '''
    Return a file for a corpus - e.g. extra metadata.
    '''

    permission_classes = [CanSearchCorpus]

    def get(self, request, *args, **kwargs):
        corpus = Corpus.objects.get(corpus_name_from_request(request))
        if not corpus.has_python_definition:
            raise NotFound()
        path = os.path.join(corpus_dir(corpus.name), 'documents', kwargs['filename'])
        if not os.path.isfile(path):
            raise NotFound()
        return FileResponse(open(path, 'rb'))


class CorpusDefinitionViewset(viewsets.ModelViewSet):
    permission_classes = [IsCurator]
    serializer_class = CorpusJSONDefinitionSerializer

    def get_queryset(self):
        return Corpus.objects.filter(has_python_definition=False)


class CorpusDataFileViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CorpusDataFileSerializer

    def get_queryset(self):
        queryset = CorpusDataFile.objects.all()

        corpus = self.request.query_params.get('corpus')
        if corpus:
            queryset = queryset.filter(corpus=corpus)

        samples = self.request.query_params.get('samples', False)
        if samples:
            queryset = queryset.filter(is_sample=True)

        return queryset.order_by('created')

    @action(detail=True, methods=['get'])
    def info(self, request, pk):
        obj = self.get_object()
        delimiter = obj.corpus.configuration_obj.source_data_delimiter

        info = get_csv_info(obj.file.path, sep=delimiter if delimiter else ',')

        return Response(info, HTTP_200_OK)
