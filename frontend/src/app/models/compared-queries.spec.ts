import { mockCorpus, mockField2 } from '../../mock-data/corpus';
import { SimpleStore } from '../store/simple-store';
import { ComparedQueries } from './compared-queries';
import { QueryModel } from './query';

fdescribe('ComparedQueries', () => {
    let store: SimpleStore;
    let query: QueryModel;
    let compared: ComparedQueries;

    beforeEach(() => {
        store = new SimpleStore();
        query = new QueryModel(mockCorpus, store);
        compared = new ComparedQueries(store);
    });

    it('should create', () => {
        expect(compared).toBeTruthy();
        expect(compared.state$.value).toEqual({ primary: undefined, compare: [] });
    });

    it('should update', () => {
        compared.setParams({ compare: ['test', 'test2'] });
        expect(compared.state$.value).toEqual({ primary: undefined, compare: ['test', 'test2'] });

        compared.reset();
        expect(compared.state$.value).toEqual({ primary: undefined, compare: [] });
    });

    it('should clean overlapping queries', () => {
        compared.setParams({ primary: undefined, compare: [ 'test', 'test2'] });

        query.setQueryText('test');
        expect(compared.state$.value).toEqual({ primary: 'test', compare: ['test2'] });
        expect(store.currentParams()['compareTerms']).toBe('test2');

        compared.setParams({ compare: ['test2', 'test3', 'test2']});
        expect(compared.state$.value).toEqual({ primary: 'test', compare: ['test2', 'test3'] });
        expect(store.currentParams()['compareTerms']).toBe('test2,test3');
    });

    it('should have all queries as an observable', () => {
        let latestValue: string[];
        compared.allQueries$.subscribe(value => latestValue = value);

        expect(latestValue).toEqual([undefined]);

        compared.setParams({compare: ['test2']});
        expect(latestValue).toEqual([undefined, 'test2']);

        query.setQueryText('test');
        expect(latestValue).toEqual(['test', 'test2']);
    });

    it('it should initialise from parameters', () => {
        store = new SimpleStore();
        store.paramUpdates$.next({
            query: 'test',
            compareTerms: 'test2,test3,test4'
        });

        query = new QueryModel(mockCorpus, store);
        compared = new ComparedQueries(store);

        expect(query.state$.value.queryText).toEqual('test');
        expect(compared.state$.value).toEqual({primary: 'test', compare: ['test2', 'test3', 'test4']});

    });

    it('should set from parameters', () => {
        store.paramUpdates$.next({
            compareTerms: 'test,test2'
        });
        expect(compared.state$.value).toEqual({primary: undefined, compare: ['test', 'test2']});


        store.paramUpdates$.next({
            query: 'different test',
        });
        // compared queries are reset when query text changes
        expect(query.state$.value.queryText).toEqual('different test');
        expect(compared.state$.value).toEqual({primary: 'different test', compare: ['test', 'test2']});
    });

    it('should not reset the query when destroyed', () => {
        store.paramUpdates$.next({
            query: 'test',
            compareTerms: 'test2,test3,test4'
        });

        compared.complete();
        expect(store.currentParams()).toEqual({ query: 'test' });
    });
});
