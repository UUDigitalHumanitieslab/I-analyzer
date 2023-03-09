/* eslint-disable @typescript-eslint/naming-convention */
import { BehaviorSubject } from 'rxjs';
import { findByName } from '../app/utils/utils';
import { BooleanFilterOptions } from '../app/models/search-filter-options';
import { Corpus, CorpusField } from '../app/models';

const mockFilterOptions: BooleanFilterOptions = {
    checked: false,
    name: 'BooleanFilter',
    description: 'Use this filter to decide whether or not this field is great',
};

/** a keyword field with a boolean filter */
export const mockField = new CorpusField({
    name: 'great_field',
    description: 'A really wonderful field',
    display_name: 'Greatest field',
    display_type: 'keyword',
    es_mapping: {type: 'keyword'},
    hidden: false,
    sortable: false,
    primary_sort: false,
    searchable: false,
    downloadable: false,
    search_filter: mockFilterOptions,
    results_overview: true,
    search_field_core: true,
    csv_core: true,
    visualizations: [],
    visualization_sort: null,
    indexed: true,
    required: false,
});

/** a text content field */
export const mockField2 = new CorpusField({
    name: 'speech',
    description: 'A content field',
    display_name: 'Speechiness',
    display_type: 'text',
    es_mapping: {type: 'text'},
    hidden: false,
    sortable: false,
    primary_sort: false,
    searchable: true,
    downloadable: true,
    search_filter: null,
    results_overview: true,
    search_field_core: true,
    csv_core: true,
    visualizations: [],
    visualization_sort: null,
    indexed: true,
    required: false,
});

/** a keyword field with sorting option */
export const mockField3 = new CorpusField({
    name: 'ordering',
    description: 'A field which can be sorted on',
    display_name: 'Sort me',
    display_type: 'integer',
    es_mapping: {type: 'keyword'},
    hidden: false,
    sortable: true,
    primary_sort: false,
    searchable: false,
    downloadable: true,
    results_overview: true,
    search_filter: null,
    search_field_core: false,
    csv_core: true,
    visualizations: [],
    visualization_sort: null,
    indexed: true,
    required: false,
});

/** a date field */
export const mockFieldDate = new CorpusField({
    name: 'date',
    display_name: 'Date',
    description: '',
    display_type: 'date',
    hidden: false,
    sortable: true,
    primary_sort: false,
    searchable: false,
    downloadable: true,
    search_filter: {
        name: 'DateFilter',
        lower: '1800-01-01',
        upper: '1899-12-31',
        description: ''
    },
    es_mapping: {type: 'date'},
    results_overview: true,
    search_field_core: false,
    csv_core: true,
    visualizations: [],
    visualization_sort: null,
    indexed: true,
    required: false,
});


export const mockCorpus: Corpus = {
    name: 'test1',
    serverName: 'default',
    index: 'test1',
    title: 'Test corpus',
    description: 'This corpus is for mocking',
    minDate: new Date(),
    maxDate: new Date(),
    image: 'test.jpg',
    scan_image_type: 'pdf',
    allow_image_download: false,
    word_models_present: false,
    fields: [mockField]
};

export const mockCorpus2: Corpus = {
    name: 'test2',
    serverName: 'default',
    index: 'test2',
    title: 'Test corpus 2',
    description: 'This corpus is for mocking',
    minDate: new Date(),
    maxDate: new Date(),
    image: 'test.jpg',
    scan_image_type: 'pdf',
    allow_image_download: false,
    word_models_present: false,
    fields: [mockField2]
};

export class CorpusServiceMock {
    private currentCorpusSubject = new BehaviorSubject<Corpus>(mockCorpus);
    public currentCorpus = this.currentCorpusSubject.asObservable();

    public get(refresh=false): Promise<Corpus[]> {
        return Promise.resolve([mockCorpus, mockCorpus2]);
    }

    public set(corpusName='test1'): Promise<boolean> {
        return this.get().then(all => {
            const corpus = findByName(all, corpusName);
            if (!corpus) {
                return false;
            } else {
                this.currentCorpusSubject.next(corpus);
                return true;
            }
        });
    }

}
