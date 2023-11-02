import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';
import * as _ from 'lodash';
import { mockCorpus, mockField } from '../../mock-data/corpus';
import { commonTestBed } from '../common-test-bed';

import { CorpusField, FoundDocument, QueryModel } from '../models/index';

import { SearchResultsComponent } from './search-results.component';
import { makeDocument } from '../../mock-data/constructor-helpers';
import { DocumentPage, PageResults } from '../models/page-results';
import { of } from 'rxjs';
import { By } from '@angular/platform-browser';

const createField = (name: string): CorpusField => {
    const field = _.cloneDeep(mockField);
    field.name = name;
    return field;
};

const documents: FoundDocument[] = [
    makeDocument(
        {
            a: '1',
            b: '2',
            c: 'Hide-and-seek!'
        }, mockCorpus, '1', 1,
        {
            c: ['Where is <span>Wally?</span>', 'I cannot find <span>Wally</span> anywhere!']
        }
    ),
    makeDocument(
        {
            a: '3',
            b: '4',
            c: 'Wally is here'
        }, mockCorpus, '2', 0.5
    )
];

const fields = ['a', 'b', 'c'].map(createField);

class MockResults extends PageResults {
    fetch() {
        const page = new DocumentPage(documents, 2, fields);
        return of(page);
    }
}

describe('Search Results Component', () => {
    let component: SearchResultsComponent;
    let fixture: ComponentFixture<SearchResultsComponent>;

    beforeEach(waitForAsync(() => {
        commonTestBed().testingModule.compileComponents();
    }));

    beforeEach(() => {
        fixture = TestBed.createComponent(SearchResultsComponent);

        component = fixture.componentInstance;
    });

    beforeEach(() => {
        const corpus = _.merge(mockCorpus, fields);
        const query = new QueryModel(corpus);
        query.setQueryText('wally');
        query.setHighlight(10);
        component.queryModel = query;
        fixture.detectChanges();
        component.pageResults = new MockResults(undefined, component.queryModel);
    });


    it('should be created', () => {
        expect(component).toBeTruthy();
    });

    it('should show a loading spinner on opening', () => {
        const loadingElement = fixture.debugElement.query(
            By.css('.is-loading')
        );
        expect(loadingElement).toBeTruthy();
    });

    it('should render result', async () => {
        await fixture.whenStable();
        fixture.detectChanges();

        const element = fixture.debugElement;

        const docs = element.queryAll(
            By.css('article')
        );
        expect(docs.length).toBe(2);

        expect(element.nativeElement.innerHTML).toContain('Wally is here');
    });
});

