import { Params } from '@angular/router';
import * as _ from 'lodash';
import { Observable } from 'rxjs';
import { Corpus, CorpusField, EsFilter, FilterInterface, User, } from '../models/index';
import { EsQuery } from '../models';
import { combineSearchClauseAndFilters,  } from '../utils/es-query';
import {
    omitNullParameters, queryFiltersToParams,
    queryFromParams, searchFieldsFromParams
} from '../utils/params';
import { isFieldFilter, SearchFilter } from './field-filter';
import { isTagFilter, TagFilter } from './tag-filter';
import { makeTagSpecification } from '../utils/api-query';
import { APIQuery } from './search-requests';
import { Store } from '../store/types';
import { SimpleStore } from '../store/simple-store';
import { StoreSync } from '../store/store-sync';
import { distinctUntilChanged, map, skip, takeUntil } from 'rxjs/operators';

/** This is the query object as it is saved in the database.*/
export class QueryDb {
    /**
     * The query id, when `undefined` it will automatically assign one on save.
     */
    public id?: number;

    /**
     * JSON string representing the query model (i.e., query text and filters, see below).
     */
    public query_json: APIQuery;
    public queryModel?: QueryModel;

    /**
     * Time the first document was sent.
     */
    public started?: Date;

    /**
     * Time the last document was sent, if not aborted.
     */
    public completed?: Date;

    /**
     * Whether the download was prematurely ended.
     */
    public aborted = false;

    /**
     * Number of transferred (e.g. actually downloaded) documents. Note that this does not say anything about the size of those documents.
     */
    public transferred = 0;

    /**
     * Number of total results available for the query.
     */
    public total_results: number;

    constructor(
        apiQuery: APIQuery,
        /**
         * Name of the corpus for which the query was performed.
         */
        public corpus: string,

        /**
         * User that performed this query.
         */
        public user: number
    ) {
        this.query_json = apiQuery;
    }
}

/** These are the from / size parameters emitted by the pagination component */
export interface SearchParameters {
    from: number;
    size: number;
}

interface QueryState {
    queryText?: string;
    searchFields?: CorpusField[];
}


export class QueryModel extends StoreSync<QueryState> {
    corpus: Corpus;
    filters: FilterInterface[];
    isAuthenticated: boolean;

    update: Observable<void>;

    protected keysInStore = ['query', 'fields'];

    constructor(corpus: Corpus, isAuthenticated?: boolean, store?: Store) {
        super(store || new SimpleStore());
		this.corpus = corpus;
        this.isAuthenticated = isAuthenticated;
        this.connectToStore();
        this.filters = this.makeFilters(this.store);
        this.update = this.collectUpdates$();
    }

    get queryText(): string {
        return this.state$.value.queryText;
    }

    get searchFields(): CorpusField[] {
        return this.state$.value.searchFields;
    }

    get activeFilters() {
        return this.filters.filter(f => f.state$.value.active);
    }

    private get fieldFilters(): SearchFilter[] {
        return this.filters.filter(isFieldFilter);
    }

	setQueryText(text?: string) {
        this.setParams({ queryText: text || undefined});
	}

    addFilter(filter: FilterInterface) {
        this.setFilter(filter);
	}

    removeFilter(filter: SearchFilter) {
        this.deactivateFiltersForField(filter.corpusField);
    }

    /** get an active search filter on this query for the field (undefined if none exists) */
    filterForField(field: CorpusField): SearchFilter {
        return this.fieldFilters.find(filter => filter.corpusField.name === field.name);
    }

    /** remove all filters that apply to a corpus field */
    deactivateFiltersForField(field: CorpusField) {
        this.fieldFilters.filter(filter =>
            filter.corpusField.name === field.name
        ).forEach(filter =>
            filter.deactivate()
        );
    }

    /**
     * make a clone of the current query.
     *
     * optionally provide a store for the new model's state; if none is provided,
     * a new SimpleStore will be created
     */
    clone(store?: Store) {
        store = store || new SimpleStore();
        store.paramUpdates$.next(this.toQueryParams());
        return new QueryModel(this.corpus, this.filters.find(isTagFilter) !== undefined, store);
	}

    /**
     * convert the query to a a parameter map, for deep linking
     *
     * Unlike stateToStore(), this:
     * - only includes explicit properties, it doesn't list null values
     * - includes the parameters for filters
     */
    toQueryParams(): Params {
        const queryParams = this.stateToStore(this.state$.value);
        const filterParams = queryFiltersToParams(this);
        const params = {...queryParams,...filterParams};
        return omitNullParameters(params);
    }

    /** convert the query to an elasticsearch query */
	toEsQuery(): EsQuery {
        const state = this.state$.value;
        const filters = this.activeFilters
            .filter(isFieldFilter)
            .map(filter => filter.toEsFilter()) as EsFilter[];
        return combineSearchClauseAndFilters(state.queryText, filters, state.searchFields);
    }

    toAPIQuery(): APIQuery {
        const esQuery = this.toEsQuery();
        let tags = {};
        if (this.filters.find(isTagFilter)) {
            tags = makeTagSpecification(this.filters);
        }
        return {
            // eslint-disable-next-line @typescript-eslint/naming-convention
            es_query: esQuery,
            ...tags,
        };
    }

    protected stateToStore(state: QueryState): Params {
        const queryTextParams =  { query: state.queryText || null };
        const searchFieldsParams = { fields: state.searchFields?.map(f => f.name).join(',') || null};

        return {
            ...queryTextParams,
            ...searchFieldsParams,
        };
    }

    protected storeToState(params: Params): QueryState {
        const queryText = queryFromParams(params);
        const searchFields = searchFieldsFromParams(params, this.corpus);
        return { queryText, searchFields };
    }

    /**
     * @param store: Store
     * @returns fieldFilters: FilterInterface[]
     * if user is logged in, these include a TagFilter
     */
    private makeFilters(store: Store): FilterInterface[] {
        const fieldFilters: FilterInterface[] = this.corpus.fields.map(field => field.makeSearchFilter(store));
        if (this.isAuthenticated) {
            const tagFilter = new TagFilter(store);
        return [...fieldFilters, tagFilter];
        }
        return fieldFilters;
    }

    private setFilter(newFilter: FilterInterface): void {
        let currentFilter: FilterInterface;
        if (isTagFilter(newFilter)) {
            currentFilter = this.filters.find(isTagFilter);
        } else if (isFieldFilter(newFilter)) {
            currentFilter = this.filterForField(newFilter.corpusField);
        }
        currentFilter?.set(newFilter.currentData);
    }

    /**
     * Returns an observable of each moment when the subset of requested documents
     * changes during the lifetime of this QueryModel instance. This does not include the
     * initialisation or completion of the instance.
     *
     * The observable does not include a payload, but it can be observed by other models
     * to know when they need to fetch results
     */
    private collectUpdates$(): Observable<void> {
        // all keys in the store that determine the query, i.e. the subset of
        // documents in the corpus that it defines. These are the queryModel's
        // own stored keys and the keys stored its attached filters
        const keys = _.flatten([
            this.keysInStore,
            this.filters.map(filter => filter.keyInStore)
        ]);

        // pipe changes to the store...
        return this.store.params$.pipe(
            takeUntil(this.complete$),
            // only include outputs where the parameters have actually changed;
            // pick relevant keys and use _.isEqual for deep comparison
            distinctUntilChanged(_.isEqual, params => _.pick(params, keys)),
            // ignore the first update (which happens on initialisation)
            skip(1),
            // map to void (to match expected output type)
            map(() => undefined),
        );
    }
}
