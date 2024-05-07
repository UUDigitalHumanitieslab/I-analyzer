import { ParamMap, Params, convertToParamMap } from '@angular/router';
import * as _ from 'lodash';
import { Corpus, CorpusField, FilterInterface, QueryModel, SearchFilter, SortBy, SortDirection, SortState } from '../models';
import { TagFilter } from '../models/tag-filter';
import { PageParameters, PageResultsParameters, RESULTS_PER_PAGE } from '../models/page-results';
import { findByName } from './utils';
import { SimpleStore } from '../store/simple-store';

// general utility functions

/** omit keys that mapp to null */
export const omitNullParameters = (params: {[key: string]: any}): {[key: string]: any} => {
    const nullKeys = _.keys(params).filter(key => params[key] === null);
    return _.omit(params, nullKeys);
};

export const mergeParams = (current: Params, next: Params): Params =>
    _.assign(_.clone(current), next);

export const mergeAllParams = (values: Params[]): Params =>
    _.reduce(values, mergeParams);

// conversion between models and parameters

export const queryFromParams = (params: Params): string =>
    params['query'];

export const queryToParams = (queryText: string): Params => ({
     query: queryText || null
});

export const searchFieldsFromParams = (params: Params, corpus: Corpus): CorpusField[] => {
    if (params['fields']) {
        const fieldNames = params['fields'].split(',');
        return corpus.fields.filter(field => fieldNames.includes(field.name));
    }
};

// highlight

export const highlightToParams = (highlight?: number): { highlight: string | null } => {
    if (_.isUndefined(highlight)) {
        return { highlight: null };
    }

    return { highlight: highlight.toString() };
};

export const highlightFromParams = (params: Params): number =>
    Number(params['highlight']) || undefined;

// sort

export const sortSettingsToParams = (sortBy: SortBy, direction: SortDirection, corpus: Corpus): {sort: string|null} => {
    if (_.isEqual([sortBy, direction], corpus.defaultSort)) {
        return { sort: null };
    }

    let sortByName: string;
    if (!sortBy) {
        sortByName = 'relevance';
    } else {
        sortByName = sortBy.name;
    }
    return { sort: `${sortByName},${direction}` };
};

export const sortSettingsFromParams = (params: Params|undefined, corpus: Corpus): SortState => {
    if (params && !params['sort']) {
        return corpus.defaultSort;
    } else {
        const [sortParam, ascParam] = params['sort'].split(',');

        let sortBy: SortBy;

        if ( sortParam === 'relevance' ) {
            sortBy = undefined;
        } else {
            sortBy = findByName(corpus.fields, sortParam);
        }

        const sortDirection: SortDirection = ascParam;
        return [sortBy, sortDirection];
    }
};

// pagination

export const pageToParams = (state: PageParameters): Params => {
    const page = 1 + _.floor(state.from / state.size);

    if (page === 1) {
        return {
            p: null,
        };
    }

    return {p: page};
};

export const pageFromParams = (params: Params|undefined): PageParameters => {
    if (params && params['p']) {
        const page = _.toInteger(params['p']);
        const size = RESULTS_PER_PAGE;
        const from = (page - 1) * size;
        return {from, size};
    } else {
        return {
            from: 0,
            size: RESULTS_PER_PAGE,
        };
    }
};

// filters

export const filtersFromParams = (params: ParamMap, corpus: Corpus): FilterInterface[] => {
    const fieldFilters = fieldFiltersFromParams(params, corpus);
    const tagFilter = tagFilterFromParams(params);
    return [...fieldFilters, tagFilter];
};

const fieldFiltersFromParams = (params: ParamMap, corpus: Corpus): SearchFilter[] => {
    const specifiedFields = corpus.fields.filter(field => params.has(field.name));
    return specifiedFields.map(field => {
        const filter = field.makeSearchFilter();
        filter.storeToState(params);
        return filter;
    });
};

const tagFilterFromParams = (params: ParamMap): TagFilter => {
    const store = new SimpleStore();
    const filter = new TagFilter(store);
    filter.storeToState(params);
    return filter;
};

export const queryFiltersToParams = (queryModel: QueryModel) => {
    const filterParamsPerField = queryModel.filters.map(filter =>
        filter.stateToStore(filter.state$.value)
    );
    return _.reduce(
        filterParamsPerField,
        _.merge,
        {}
    );
};

// utilities

export const pageResultsParametersToParams = (state: PageResultsParameters, corpus: Corpus): Params => {
    const sort = sortSettingsToParams(...state.sort, corpus);
    const highlight = highlightToParams(state.highlight);
    const page = pageToParams(state);
    return {...sort, ...highlight, ...page};
};

export const pageResultsParametersFromParams = (params: Params, corpus: Corpus): PageResultsParameters => ({
    sort: sortSettingsFromParams(params, corpus),
    highlight: highlightFromParams(params),
    ...pageFromParams(params)
});
