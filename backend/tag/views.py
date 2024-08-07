from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from django.http import HttpRequest
from rest_framework.exceptions import NotFound, PermissionDenied

from .models import Tag, TaggedDocument
from .permissions import IsTagOwner
from .serializers import TagSerializer
from addcorpus.models import Corpus
from addcorpus.permissions import CanSearchCorpus

def check_corpus_name(request: HttpRequest):
    '''
    Returns the name of the corpus specified in the request query parameters,
    if there is one.

    Raises 404 if this corpus does not exist.
    '''

    corpus_name = request.query_params.get('corpus', None)
    if corpus_name and not Corpus.objects.filter(name=corpus_name):
        raise NotFound(f'corpus {corpus_name} does not exist')
    return corpus_name

class TagViewSet(ModelViewSet):
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated, IsTagOwner]
    queryset = Tag.objects.all()

    def perform_create(self, serializer):
        '''Overwrites ModelViewSet.perform_create
        Auto-assigns the authenticated user on creation'''
        return serializer.save(user=self.request.user)

    def list(self, *args, **kwargs):
        '''Overwrites ModelViewSet.list
        Filters the default queryset by ownership.
        Only applies to list view, the class queryset is unaffected.

        Supports filtering on a corpus by specifying the name as a query parameter.
        '''


        filters = {
            'user': self.request.user,
        }

        corpus_name = check_corpus_name(self.request)
        if corpus_name:
            filters.update({
                'tagged_docs__corpus__name': corpus_name
            })

        queryset = self.queryset.filter(**filters).distinct()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class DocumentTagsView(APIView):
    permission_classes = [IsAuthenticated, CanSearchCorpus]

    def get(self, request, *args, **kwargs):
        '''
        Get the tags for a document
        '''

        doc = self._get_document(**kwargs)

        if doc:
            data = self._serialize(request, doc)
        else:
            data = {
                **kwargs,
                'tags': [],
            }

        return Response(data)

    def patch(self, request, *args, **kwargs):
        '''
        Edit a document's tags.
        '''

        corpus = Corpus.objects.get(name=kwargs.get('corpus'))
        doc_id = kwargs.get('doc_id')
        doc, _ = TaggedDocument.objects.get_or_create(
            corpus=corpus,
            doc_id=doc_id
        )

        # check that the request is not patching readonly properties
        readonly = {'corpus', 'doc_id'}
        if set.intersection(readonly, request.data.keys()):
            raise PermissionDenied('Patching the corpus or ID of documents is not allowed')

        # verify tags
        tag_ids = request.data.get('tags')
        for tag_id in tag_ids:
            self._verify_tag(request, tag_id)

        # update tags for the user
        current_tags = doc.tags.filter(user = request.user)
        new_tags = Tag.objects.filter(id__in=tag_ids, user=request.user)

        for tag in current_tags.difference(new_tags):
            doc.tags.remove(tag)

        for tag in new_tags.difference(current_tags):
            doc.tags.add(tag)

        return Response(self._serialize(request, doc))

    def _get_document(self, **kwargs):
        match = TaggedDocument.objects.filter(
            corpus__name=kwargs.get('corpus'),
            doc_id=kwargs.get('doc_id'),
        )

        if match.exists():
            return match.first()

    def _verify_tag(self, request, tag_id):
        if not Tag.objects.filter(id=tag_id).exists():
            raise NotFound(f'Tag {tag_id} does not exist')

        tag = Tag.objects.get(id=tag_id)

        if not tag.user == request.user:
            raise PermissionDenied(f'You do not have permission to modify tag {tag_id}')

    def _serialize(self, request, doc: TaggedDocument):
        tags = doc.tags.filter(user=request.user)
        serializer = TagSerializer(tags, many=True)
        return {
            'corpus': doc.corpus.name,
            'id': doc.doc_id,
            'tags': serializer.data
        }
