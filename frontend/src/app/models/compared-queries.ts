import { Params } from '@angular/router';
import { StoreSync } from '../store/store-sync';
import * as _ from 'lodash';

interface CompareQueryState {
    queries: string[];
}

const COMPARE_TERMS_KEY = 'compareTerms';
const DELIMITER = ',';

export class ComparedQueries extends StoreSync<CompareQueryState> {
    protected keysInStore = [COMPARE_TERMS_KEY];

    constructor(store) {
        super(store);
        this.connectToStore();
    }

    reset() {
        this.setParams({ queries: [] });
    }

    protected storeToState(params: Params): CompareQueryState {
        const value = _.get(params, COMPARE_TERMS_KEY, '');
        if (value.length) {
            return { queries: value.split(DELIMITER) };
        } else {
            return { queries: [] };
        }
    }

    protected stateToStore(state: CompareQueryState): Params {
        if (!state.queries.length) {
            const value = state.queries.join(DELIMITER);
            return { [COMPARE_TERMS_KEY]: value };
        } else {
            return { [COMPARE_TERMS_KEY]: null };
        }
    }
}
