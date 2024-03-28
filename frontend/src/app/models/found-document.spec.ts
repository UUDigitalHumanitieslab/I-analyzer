import { TestBed, waitForAsync } from '@angular/core/testing';
import { makeDocument } from '../../mock-data/constructor-helpers';
import { mockCorpus, mockCorpus3 } from '../../mock-data/corpus';
import { FoundDocument } from './found-document';
import { TagService } from '../services/tag.service';
import { TagServiceMock, mockTags } from '../../mock-data/tag';
import * as _ from 'lodash';
import { reduce, take } from 'rxjs/operators';
import { Observable } from 'rxjs';
import { Tag } from './tag';

const maxScore = 2.9113607;
const mockResponse = {
    _index: 'troonredes',
    _id: '1994_troonrede',
    _score: 2.9113607,
    _source: {
        date: '1994-09-20',
        id: '1994_troonrede',
        title: 'Troonrede 20 september 1994',
        monarch: 'Beatrix',
        speech_type: 'troonrede',
        content: 'Om op langere termijn de zekerheid te kunnen blijven bieden ' +
            'van een gegarandeerd basispensioen, en om solidaire regelingen bij ' +
            'arbeidsongeschiktheid en werkloosheid in stand te houden, is een ' +
            'kritische toets van het bestaande stelsel nu geboden.'
    },
    highlight: {
        content: [
            '<em>toets</em>'
        ]
    }
};

describe('FoundDocument', () => {
    let tagService: TagService;

    beforeEach(() => {
        TestBed.configureTestingModule({
            providers: [
                { provide: TagService, useValue: new TagServiceMock() }
            ]
        });
        tagService = TestBed.inject(TagService);
    });

    it('should construct from an elasticsearch response', () => {
        const document = new FoundDocument(mockCorpus, mockResponse, maxScore, tagService);

        expect(document.id).toBe('1994_troonrede');
        expect(document.fieldValues['monarch']).toBe('Beatrix');
    });

    it('should reflect context', () => {
        const notDefinedInCorpus = makeDocument({great_field: 'test'}, mockCorpus);
        expect(notDefinedInCorpus.hasContext).toBeFalse();

        const missingValues = makeDocument({great_field: 'test'}, mockCorpus3);
        expect(missingValues.hasContext).toBeFalse();

        const shouldHaveContext = makeDocument({
            great_field: 'test',
            date: new Date('1800-01-01')
        }, mockCorpus3);
        expect(shouldHaveContext.hasContext).toBeTrue();
    });

    it('should set tags', waitForAsync(() => {
        const doc = makeDocument({ great_field: 'test' });

        const tags$: Observable<Tag[][]> = doc.tags$.pipe(
            take(3),
            reduce(
                (accumulated, current) => [...accumulated, current],
                [],
            ),
        );

        const tag1 = _.first(mockTags);
        const tag2 = _.last(mockTags);

        doc.removeTag(tag1);
        doc.addTag(tag1);

        tags$.subscribe(allTags => {
            expect(allTags).toEqual([
                [tag1, tag2],
                [tag2],
                [tag1, tag2]
            ]);
        });
    }));
});
