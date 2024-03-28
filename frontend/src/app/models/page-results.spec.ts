import { TestBed, inject, waitForAsync } from '@angular/core/testing';
import { SearchService } from '../services/search.service';
import { PageResults } from './page-results';
import { QueryModel } from './query';
import { mockCorpus, mockField } from '../../mock-data/corpus';
import { SimpleStore } from '../store/simple-store';
import { take } from 'rxjs/operators';
import { SearchServiceMock } from '../../mock-data/search';

describe('PageResults', () => {
    let store: SimpleStore;
    let queryModel: QueryModel;
    let results: PageResults;
    let service: SearchService;

    beforeEach(() => {
        TestBed.configureTestingModule({
            providers: [
                { provide: SearchService, useValue: new SearchServiceMock() },
            ],
        });
    });

    beforeEach(inject([SearchService], (searchService: SearchService) => {
        store = new SimpleStore();
        service = searchService;
        queryModel = new QueryModel(mockCorpus, true, store);
        service = searchService;
        results = new PageResults(store, searchService, queryModel);
    }));

    it('should be created', () => {
        expect(results).toBeTruthy();
    });

    it('should load from parameters', () => {
        store.paramUpdates$.next({
            query: 'test',
            highlight: '200',
        });
        queryModel = new QueryModel(mockCorpus, true, store);
        results = new PageResults(store, service, queryModel);
        expect(results.state$.value.highlight).toBe(200);
    });

    it('should set the sort state', () => {
        results.setSortBy(mockField);
        expect(results.state$.value.sort).toEqual([mockField, 'desc']);

        results.setSortDirection('asc');
        expect(results.state$.value.sort).toEqual([mockField, 'asc']);

        results.setSortBy(undefined);
        expect(results.state$.value.sort).toEqual([undefined, 'desc']);
    });

    it('should reset the page when changing sorting', () => {
        results.setParams({from: 20});
        expect(results.state$.value.from).toBe(20);

        results.setSortBy(mockField);
        expect(results.state$.value.from).toBe(0);

        results.setParams({from: 20});
        results.setSortDirection('asc');
        expect(results.state$.value.from).toBe(0);
    });

    it('should reset highlighting when there is no query text', () => {
        queryModel.setQueryText('test');
        results.setParams({ highlight: 200 });
        expect(results.state$.value.highlight).toBe(200);

        queryModel.setQueryText('different test');
        expect(results.state$.value.highlight).toBe(200);

        queryModel.setQueryText('');
        expect(results.state$.value.highlight).toBeUndefined();
    });

    it('should fetch results', waitForAsync(() => {
        results.result$.pipe(
            take(1)
        ).subscribe(page => {
            expect(page).toBeTruthy();
            expect(page.total).toBe(1);
        });
    }));
});
