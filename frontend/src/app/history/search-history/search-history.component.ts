import { Component, OnInit } from '@angular/core';
import { Params, Router } from '@angular/router';
import * as _ from 'lodash';
import { apiQueryToQueryModel } from '../../utils/es-query';
import { QueryDb } from '../../models/index';
import { CorpusService, QueryService } from '../../services/index';
import { HistoryDirective } from '../history.directive';
import { findByName } from '../../utils/utils';
import { actionIcons } from '../../shared/icons';

@Component({
    selector: 'ia-search-history',
    templateUrl: './search-history.component.html',
    styleUrls: ['./search-history.component.scss'],
})
export class SearchHistoryComponent extends HistoryDirective implements OnInit {
    public queries: QueryDb[];
    public displayCorpora = false;

    actionIcons = actionIcons;

    constructor(
        corpusService: CorpusService,
        private queryService: QueryService,
        private router: Router
    ) {
        super(corpusService);
    }

    async ngOnInit() {
        this.retrieveCorpora();
        this.queryService.retrieveQueries().then((searchHistory) => {
            const sortedQueries = this.sortByDate(searchHistory);
            // not using _.sortedUniqBy as sorting and filtering takes place w/ different aspects
            this.queries = _.uniqBy(
                sortedQueries,
                (query) => query.query_json
            ).map(this.addQueryModel.bind(this));
        });
    }

    addQueryModel(query?: QueryDb) {
        const corpus = findByName(this.corpora, query.corpus);
        if (corpus) {
            query.queryModel = apiQueryToQueryModel(query.query_json, corpus);
            return query;
        }
    }

    routerLink(query: QueryDb): string[] {
        return ['/search', query.corpus];
    }

    queryParams(query: QueryDb): Params {
        return query.queryModel.toQueryParams();
    }
}
