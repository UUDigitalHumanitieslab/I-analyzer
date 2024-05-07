import { mockCorpus, mockField2 } from '../../mock-data/corpus';
import { SimpleStore } from '../store/simple-store';
import { ComparedQueries } from './compared-queries';
import { QueryModel } from './query';

describe('ComparedQueries', () => {
    let store: SimpleStore;
    let query: QueryModel;
    let compared: ComparedQueries;

    beforeEach(() => {
        store = new SimpleStore();
        query = new QueryModel(mockCorpus, store);
        compared = new ComparedQueries(store, query);
    });

    it('should create', () => {
        expect(compared).toBeTruthy();
        expect(compared.state$.value).toEqual({ queries: [] });
    });

    it('should update', () => {
        compared.setParams({ queries: ['test', 'test2'] });
        expect(compared.state$.value).toEqual({ queries: ['test', 'test2'] });

        compared.reset();
        expect(compared.state$.value).toEqual({ queries: [] });
    });

    it('should reset when the query text changes', () => {
        compared.setParams({ queries: [ 'test', 'test2'] });

        query.setParams({ searchFields: [mockField2] });
        expect(compared.state$.value).toEqual({ queries: ['test', 'test2'] });

        query.setQueryText('test');
        expect(compared.state$.value).toEqual({ queries: [] });
    });

    it('should have all queries as an observable', () => {
        let latestValue: string[];
        compared.allQueries$.subscribe(value => latestValue = value);

        expect(latestValue).toEqual([undefined]);

        compared.setParams({queries: ['test2']});
        expect(latestValue).toEqual([undefined, 'test2']);

        query.setQueryText('test');
        expect(latestValue).toEqual(['test']);

        compared.setParams({queries: ['test2']});
        expect(latestValue).toEqual(['test', 'test2']);
    });

    it('it should initialise from parameters', () => {
        store = new SimpleStore();
        store.paramUpdates$.next({
            query: 'test',
            compareTerms: 'test2,test3,test4'
        });

        query = new QueryModel(mockCorpus, store);
        compared = new ComparedQueries(store, query);

        expect(query.state$.value.queryText).toEqual('test');
        expect(compared.state$.value).toEqual({queries: ['test2', 'test3', 'test4']});

    });

    it('should set from parameters', () => {
        store.paramUpdates$.next({
            compareTerms: 'test,test2'
        });
        expect(compared.state$.value).toEqual({queries: ['test', 'test2']});


        store.paramUpdates$.next({
            query: 'different test',
        });
        // compared queries are reset when query text changes
        expect(query.state$.value.queryText).toEqual('different test');
        expect(compared.state$.value).toEqual({queries: []});
    });
});
