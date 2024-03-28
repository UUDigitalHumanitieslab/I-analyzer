// these functions are shorthands to create objects that would normally come out the API

import { Corpus, FieldValues, FoundDocument, HighlightResult, SearchHit } from '../app/models';
import { mockCorpus } from './corpus';
import { TagServiceMock } from './tag';

const tagService = new TagServiceMock() as any;

export const makeDocument = (
    fieldValues: FieldValues,
    corpus: Corpus = mockCorpus,
    id: string = '0',
    relevance: number = 1,
    createTags: boolean = true,
    highlight: HighlightResult = undefined
): FoundDocument => {
    const hit: SearchHit = {
        _id: id, _score: relevance, _source: fieldValues, highlight
    };
    if (createTags) {
        return new FoundDocument(corpus, hit, 1, tagService);
    }
    return new FoundDocument(corpus, hit, 1);
};

