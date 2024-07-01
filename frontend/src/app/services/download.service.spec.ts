import { TestBed, inject } from '@angular/core/testing';

import { ApiService } from './api.service';
import { ApiServiceMock } from '../../mock-data/api';
import { DownloadService } from './download.service';
import { mockCorpus, mockField } from '../../mock-data/corpus';
import { DownloadOptions, LimitedResultsDownloadParameters, QueryModel, SortState } from '../models';

describe('DownloadService', () => {
    let apiService: ApiService;
    let service: DownloadService;

    beforeEach(() => {
        TestBed.configureTestingModule({
            providers: [
                { provide: ApiService, useValue: new ApiServiceMock() },
                DownloadService,
            ]
        });
    });

    beforeEach(inject([ApiService, DownloadService], (api, download) => {
        service = download;
        apiService = api;
    }));

    it('should be created', () => {
        expect(service).toBeTruthy();
    });

    it('should make a download request', () => {
        const query = new QueryModel(mockCorpus);
        query.setQueryText('test');

        const size = 1;
        const route = `/search/${query.corpus.name}`;
        const sort: SortState = [mockField, 'desc'];
        const highlight = 200;
        const options: DownloadOptions = {
            encoding: 'utf-8',
        };

        spyOn(apiService, 'download').and.returnValue(Promise.resolve({}));
        service.download(query.corpus, query, query.corpus.fields, size, route, sort, highlight, options);
        const expectedBody: LimitedResultsDownloadParameters = {
            corpus: mockCorpus.name,
            fields: ['great_field', 'speech'],
            route,
            es_query: {
                query: {
                    bool: {
                        must: {
                            simple_query_string: {
                                query: 'test',
                                lenient: true,
                                default_operator: 'or',
                            },
                        },
                        filter: [],
                    },
                },
                sort: [{ great_field: 'desc' }],
                highlight: {
                    fragment_size: highlight,
                    pre_tags: ['<span class="highlight">'],
                    post_tags: ['</span>'],
                    order: 'score',
                    fields: [{ speech: {} }],
                },
                from: 0,
                size,
            },
            encoding: 'utf-8',
        };
        expect(apiService.download).toHaveBeenCalledWith(expectedBody);
    });
});
