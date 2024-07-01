// these functions are shorthands to create objects that would normally come out the API

import { Corpus, FieldValues, FoundDocument, HighlightResult, SearchHit } from '../app/models';
import { mockCorpus } from './corpus';
import { TagServiceMock } from './tag';
import { EntityServiceMock } from './entity';

const tagService = new TagServiceMock() as any;
const entityService = new EntityServiceMock() as any;

export const makeDocument = (
    fieldValues: FieldValues,
    corpus: Corpus = mockCorpus,
    id: string = '0',
    relevance: number = 1,
    highlight: HighlightResult = undefined
): FoundDocument => {
    const hit: SearchHit = {
        _id: id, _score: relevance, _source: fieldValues, highlight
    };
    return new FoundDocument(tagService, entityService, corpus, hit);
};

