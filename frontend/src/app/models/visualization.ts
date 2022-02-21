import { AggregateResult, DateResult } from '.';
import { SearchFilter, SearchFilterData } from './search-filter';

// the corpusFields has an array of visualizations
// the visualizationField represents one pairing of corpus field + visualization
export type visualizationField = {
    name: string,
    visualization: string,
    displayName?: string,
    visualizationSort?: string,
    searchFilter?: SearchFilter<SearchFilterData> | null,
    multiFields?: string[];
};

export type HistogramSeriesRaw = {
    data: AggregateResult[],
    total_doc_count: number,
    searchRatio: number,
    queryText?: string,
};

export type TimelineSeriesRaw = {
    data: DateResult[],
    total_doc_count: number,
    searchRatio: number,
    queryText?: string,
};

export type freqTableHeaders = {
    key: string,
    label: string,
    format?: (value) => string|undefined,
}[];

export type histogramOptions = {
    frequencyMeasure: 'documents'|'tokens',
    normalizer: 'raw'|'percent'|'documents'|'terms',
};
