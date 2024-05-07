import { Params } from '@angular/router';
import { StoreSync } from '../store/store-sync';
import * as _ from 'lodash';
import { Store } from '../store/types';
import { Observable } from 'rxjs';
import { queryFromParams, queryToParams } from '../utils/params';
import { map } from 'rxjs/operators';

interface CompareQueryState {
    primary: string|undefined;
    compare: string[];
}

const COMPARE_TERMS_KEY = 'compareTerms';
const DELIMITER = ',';

export class ComparedQueries extends StoreSync<CompareQueryState> {
    /** all queries, including the primary query text */
    allQueries$: Observable<string[]>;

    protected keysInStore = ['query', COMPARE_TERMS_KEY];

    constructor(store: Store) {
        super(store);
        this.connectToStore();

        this.allQueries$ = this.state$.pipe(
            map(state => [state.primary, ...state.compare])
        );
    }

    reset() {
        this.setParams({ compare: [] });
    }

    protected storeToState(params: Params): CompareQueryState {
        const primary = queryFromParams(params);

        let compare: string[];
        if (_.get(params, COMPARE_TERMS_KEY)) {
            compare = _.get(params, COMPARE_TERMS_KEY).split(DELIMITER);
        } else {
            compare = [];
        }
        compare = _.without(compare, primary);
        return { primary, compare };
    }

    protected stateToStore(state: CompareQueryState): Params {
        const query = queryToParams(state.primary);
        let compareTerms: string;
        if (!_.isEmpty(state.compare)) {
            compareTerms = state.compare.map(encodeURIComponent).join(DELIMITER);
        } else {
            compareTerms = null;
        }
        return {...query, [COMPARE_TERMS_KEY]: compareTerms};
    }

}
