import { Params } from '@angular/router';
import { StoreSync } from '../store/store-sync';
import * as _ from 'lodash';
import { Store } from '../store/types';
import { Observable } from 'rxjs';
import { queryFromParams, queryToParams } from '../utils/params';
import { filter, map, takeUntil } from 'rxjs/operators';

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

        this.cleanStoredState();

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
            compare = this.cleanComparedQueries(
                primary,
                params[COMPARE_TERMS_KEY].split(DELIMITER)
            );
        } else {
            compare = [];
        }
        return { primary, compare };
    }

    protected stateToStore(state: CompareQueryState): Params {
        const query = queryToParams(state.primary);
        let compareTerms: string;
        if (!_.isEmpty(state.compare)) {
            compareTerms = this.cleanComparedQueries(state.primary, state.compare).join(DELIMITER);
        } else {
            compareTerms = null;
        }
        return {...query, [COMPARE_TERMS_KEY]: compareTerms};
    }

    protected storeOnComplete(): Params {
        return { [COMPARE_TERMS_KEY]: null };
    }

    private cleanStoredState() {
        this.store.params$.pipe(
            takeUntil(this.complete$),
            filter(this.isDirty.bind(this)),
        ).subscribe(params => {
            this.store.paramUpdates$.next(this.stateToStore(this.storeToState(params)));
        });

    }

    /**
     * get a "cleaned" list of compared queries by removing overlapping ones
     */
    private cleanComparedQueries(primary: string, compared: string[]) {
        return _.uniq(_.without(compared, primary));
    }

    /**
     * This model does some filtering of stored queries. This function checks whether the stored
     * value contains queries that are ignored by the model (and is therefore in need of cleaning).
     */
    private isDirty(params: Params): boolean {
        if (_.has(params, COMPARE_TERMS_KEY)) {
            const stored = params[COMPARE_TERMS_KEY].split(DELIMITER);
            const cleaned = this.storeToState(params).compare;
            return !_.isEqual(stored, cleaned);
        }
        return false;
    }

}
