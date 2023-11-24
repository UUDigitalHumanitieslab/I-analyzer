import { Injectable } from '@angular/core';

import { ApiService } from './api.service';
import { ElasticSearchService } from './elastic-search.service';
import {
    Corpus, QueryModel, SearchResults,
    AggregateQueryFeedback
} from '../models/index';


@Injectable()
export class SearchService {
    constructor(
        private apiService: ApiService,
        private elasticSearchService: ElasticSearchService,
    ) {
        window['apiService'] = this.apiService;
    }

    /**
     * Load results for requested page
     */
    public async loadResults(
        queryModel: QueryModel,
        from: number,
        size: number
    ): Promise<SearchResults> {
        const results = await this.elasticSearchService.loadResults(
            queryModel,
            from,
            size
        );
        results.fields = queryModel.corpus.fields.filter((field) => field.resultsOverview);
        return results;
    }

    public async search(queryModel: QueryModel
    ): Promise<SearchResults> {
        const request = this.elasticSearchService.search(queryModel);
        return request.then(results =>
            this.filterResultsFields(results, queryModel)
        );
    }

    public async aggregateSearch(
        corpus: Corpus,
        queryModel: QueryModel,
        aggregators: any
    ): Promise<AggregateQueryFeedback> {
        return this.elasticSearchService.aggregateSearch(
            corpus,
            queryModel,
            aggregators
        );
    }

    public async dateHistogramSearch(
        corpus: Corpus,
        queryModel: QueryModel,
        fieldName: string,
        timeInterval: string
    ): Promise<AggregateQueryFeedback> {
        return this.elasticSearchService.dateHistogramSearch(
            corpus,
            queryModel,
            fieldName,
            timeInterval
        );
    }

    /** filter search results for fields included in resultsOverview of the corpus */
    private filterResultsFields(results: SearchResults, queryModel: QueryModel): SearchResults {
        return {
            fields: queryModel.corpus.fields.filter((field) => field.resultsOverview),
            total: results.total,
            documents: results.documents,
        } as SearchResults;
    }
}
