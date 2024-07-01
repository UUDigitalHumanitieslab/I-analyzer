/* eslint-disable @typescript-eslint/member-ordering */
/* eslint-disable @typescript-eslint/member-ordering */
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import {
    FoundDocument, Corpus, QueryModel, SearchResults,
    SearchHit
} from '../models/index';
import { Aggregator } from '../models/aggregation';
import * as _ from 'lodash';
import { TagService } from './tag.service';
import { APIQuery } from '../models/search-requests';
import { PageResultsParameters } from '../models/page-results';
import { resultsParamsToAPIQuery } from '../utils/es-query';
import { EntityService } from './entity.service';


@Injectable()
export class ElasticSearchService {

    constructor(private http: HttpClient, private entityService: EntityService, private tagService: TagService) {
    }

    getDocumentById(id: string, corpus: Corpus): Promise<FoundDocument> {
        const esQuery = {
            query: {
                term: {
                    _id: id,
                }
            },
            size: 1,
        };
        const body: APIQuery = { es_query: esQuery };
        return this.execute(corpus, body)
            .then(this.parseResponse.bind(this, corpus))
            .then(this.firstDocumentFromResults.bind(this));
    }

    public async aggregateSearch<Result>(
        corpusDefinition: Corpus,
        queryModel: QueryModel,
        aggregator: Aggregator<Result>
    ): Promise<Result> {
        const aggregations = {
            [aggregator.name]: aggregator.toEsAggregator()
        };
        const query = queryModel.toAPIQuery();
        const withAggregation = _.set(query, 'es_query.aggs', aggregations);
        const withSize0 = _.set(withAggregation, 'es_query.size', 0);
        const result = await this.execute(corpusDefinition, withSize0);
        return aggregator.parseEsResult(result.aggregations[aggregator.name]);
    }

    /**
     * Load results for requested page
     */
    public async loadResults(
        queryModel: QueryModel,
        params: PageResultsParameters,
    ): Promise<SearchResults> {
        const body = resultsParamsToAPIQuery(queryModel, params);

        // Perform the search
        const response = await this.execute(queryModel.corpus, body);
        return this.parseResponse(queryModel.corpus, response);
    }



    /**
     * Execute an ElasticSearch query and return a dictionary containing the results.
     */
    private async execute(corpus: Corpus, body: APIQuery) {
        const url = `/api/es/${corpus.name}/_search`;
        return this.http.post<SearchResponse>(url, body).toPromise();
    }

    /**
     * Extract relevant information from dictionary returned by ES
     *
     * @param corpus
     * @param response
     */
    private parseResponse(corpus: Corpus, response: SearchResponse): SearchResults {
        const hits = response.hits.hits;
        return {
            documents: hits.map(hit => this.hitToDocument(corpus, hit, response.hits.max_score)),
            total: response.hits.total
        };
    }

    private firstDocumentFromResults(results: SearchResults): FoundDocument {
        if (results.documents.length) {
            return _.first(results.documents);
        }
    }

    /**
     * return the id, relevance and field values of a given document
     */
    private hitToDocument(corpus: Corpus, hit: SearchHit, maxScore: number): FoundDocument {
        return new FoundDocument(this.tagService, this.entityService, corpus, hit, maxScore);
    }

}

export interface SearchResponse {
    took: number;
    timed_out: boolean;
    hits: {
        total: {
            value: number;
            relation: string;
        };
        max_score: number;
        hits: Array<SearchHit>;
    };
    aggregations?: any;
}
