import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { CorpusField, SearchQuery } from '../models/index';
import { HighlightService } from '../services/highlight.service';
import { HighlightPipe } from './highlight-pipe';
import { SearchRelevanceComponent } from './search-relevance.component';
import { SearchResultsComponent } from './search-results.component';

describe('Search Results Component', () => {
    let component: SearchResultsComponent;
    let fixture: ComponentFixture<SearchResultsComponent>;

    beforeEach(async(() => {
        TestBed.configureTestingModule({
            declarations: [HighlightPipe, SearchRelevanceComponent, SearchResultsComponent],
            providers: [HighlightService]
        })
            .compileComponents();
    }));

    beforeEach(() => {
        fixture = TestBed.createComponent(SearchResultsComponent);
        component = fixture.componentInstance;
        component.results = {
            completed: true,
            fields: ['a', 'b', 'c'].map(createField),
            documents: [createDocument({
                'a': '1',
                'b': '2',
                'c': 'Hide-and-seek!'
            }, '1', 1, 1),
            createDocument({
                'a': '3',
                'b': '4',
                'c': 'Wally is here'
            }, '2', 0.5, 2)],
            retrieved: 2,
            total: 2,
<<<<<<< Updated upstream
            queryModel: {
                aborted: false,
                completed: (new Date()),
                query: {
                    'bool': {
                        'must': [],
                        'filter': [],
                    }
                },
                transferred: 0
            }
=======
            queryModel: createQueryModel()
>>>>>>> Stashed changes
        };

        fixture.detectChanges();
    });

    function createField(name: string): CorpusField {
        return {
            name,
            displayName: name,
            description: 'Description',
            displayType: 'text',
            searchFilter: null,
            hidden: false
        };
    }

    function createQueryModel(name: string): SearchQuery {
        return {
            query: {
            'bool': {
                'must': 'simple_query_string': {
                    'query':'Where is Wally?',
                    'lenient': true,
                    'default_operator': 'or'
                }
                'filter': any[],
            }
    }
    }

    function createDocument(fieldValues: { [name: string]: string }, id: string, relevance: number, position) {
        return { id, relevance, fieldValues, position };
    }

    it('should be created', () => {
        expect(component).toBeTruthy();
    });

    it('should render result', async () => {
        await fixture.whenStable();
        let compiled = fixture.debugElement.nativeElement;
        expect(compiled.innerHTML).toContain('Wally is here');
    });
});

