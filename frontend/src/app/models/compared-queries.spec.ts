import { SimpleStore } from '../store/simple-store';
import { ComparedQueries } from './compared-queries';

describe('ComparedQueries', () => {
    it('should create', () => {
        const store = new SimpleStore();
        const model = new ComparedQueries(store);
        expect(model).toBeTruthy();
        expect(model.state$.value).toEqual({ queries: [] });
    });
});
