import { Params } from '@angular/router';
import { StoreSync } from '../store/store-sync';
import * as _ from 'lodash';
import { Store } from '../store/types';
import { QueryModel } from './query';
import { map, takeUntil } from 'rxjs/operators';
import { Observable, combineLatest } from 'rxjs';

interface CompareQueryState {
    queries: string[];
}

const COMPARE_TERMS_KEY = 'compareTerms';
const DELIMITER = ',';

export class ComparedQueries extends StoreSync<CompareQueryState> {
    /** all queries, including the primary query text */
    allQueries$: Observable<string[]>;

    protected keysInStore = [COMPARE_TERMS_KEY];

    constructor(store: Store, private query: QueryModel) {
        super(store);
        this.connectToStore();

        this.query.update.pipe(
            takeUntil(this.complete$),
            map(this.assignOnQueryUpdate),
        ).subscribe((params: Partial<CompareQueryState>) =>
            this.setParams(params)
        );

        this.allQueries$ = combineLatest([this.query.state$, this.state$]).pipe(
            map(([queryState, ownState]) => [queryState.queryText, ...ownState.queries])
        );
    }

    reset() {
        this.setParams({ queries: [] });
    }

    protected storeToState(params: Params): CompareQueryState {
        const value = _.get(params, COMPARE_TERMS_KEY, '');
        if (!_.isEmpty(value)) {
            return { queries: value.split(DELIMITER) };
        } else {
            return { queries: [] };
        }
    }

    protected stateToStore(state: CompareQueryState): Params {
        if (!_.isEmpty(state.queries)) {
            const value = state.queries.join(DELIMITER);
            return { [COMPARE_TERMS_KEY]: value };
        } else {
            return { [COMPARE_TERMS_KEY]: null };
        }
    }

    private assignOnQueryUpdate(distinct: string[]): Partial<CompareQueryState> {
        if (distinct.includes('query')) {
            return { queries: [] };
        } else {
            return {};
        }
    }
}
