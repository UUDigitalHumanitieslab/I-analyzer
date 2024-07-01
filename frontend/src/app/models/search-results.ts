import { HttpErrorResponse } from '@angular/common/http';

import { CorpusField } from './corpus';
import { FoundDocument } from './found-document';
import { APIQuery } from './search-requests';
import { SortState } from './sort';
import {
    AggregateTermFrequencyParameters,
    DateTermFrequencyParameters,
    NGramRequestParameters,
    TermFrequencyResult,
} from './visualization';

export interface SearchResults {
    fields?: CorpusField[];
    documents: FoundDocument[];
    total: {
        value: number;
        relation: string;
    };
}

export interface ResultOverview {
    queryText: string;
    highlight?: number;
    sort: SortState;
    resultsCount: number;
};

export interface MostFrequentWordsResult {
    key: string;
    doc_count: number;
};


export interface GeoDocument {
    id: string;
    coordinates: {
        lat: number;
        lon: number;
    };
}

export interface DateFrequencyPair {
    date: Date;
    doc_count: number;
}

export interface DateResult {
    date: Date;
    doc_count: number;
};

export interface WordSimilarity {
    key: string;
    similarity: number;
    time?: string;
};

export interface RelatedWordsResults {
    similarities_over_time: WordSimilarity[];
    time_points: string[];
    similarities_over_time_local_top_n: WordSimilarity[][];
};

export interface NgramResults {
    words: {
        label: string;
        data: number[];
    }[];
    time_points: string[];
}

export type WordInModelResult = {
    exists: true;
} | {
    exists: false;
    similar_keys: string[];
};

export interface QueryFeedback {
    status: 'not in model'|'success'|'error'|'multiple words'|'empty';
    similarTerms?: string[];
}

export interface FieldEntities {
    [entityType: string] : string
}

export interface NamedEntitiesResult {
    annotations: {[fieldName: string]: FieldEntities[]};
}

export interface TaskResult { task_ids: string[] };

export interface TaskSuccess {
    success: true;
}

interface WorkingTask {
    status: 'working';
}

export interface SuccessfulTask<T> {
    status: 'done';
    results: T;
}

export type TasksOutcome = HttpErrorResponse | WorkingTask | SuccessfulTask<NgramResults[] | TermFrequencyResult[]>;

export type ResultsDownloadParameters = {
    corpus: string;
    fields: string[];
    route: string;
} & APIQuery;

export type TermFrequencyDownloadParameters = DateTermFrequencyParameters[] | AggregateTermFrequencyParameters[];

export type LimitedResultsDownloadParameters = ResultsDownloadParameters &
    DownloadOptions;

export type DownloadType = 'search_results' | 'aggregate_term_frequency' | 'date_term_frequency' | 'ngram';
export type DownloadStatus = 'done' | 'working' | 'error';
export type DownloadParameters = TermFrequencyDownloadParameters | ResultsDownloadParameters | NGramRequestParameters;

export interface PendingDownload {
    download_type: DownloadType;
};

export interface Download {
    id: number;
    started: Date;
    completed?: Date;
    download_type: DownloadType;
    corpus: string;
    parameters: DownloadParameters;
    filename?: string;
    status: DownloadStatus;
}

export interface DownloadOptions {
    table_format?: 'long'|'wide';
    encoding: 'utf-8'|'utf-16';
};
