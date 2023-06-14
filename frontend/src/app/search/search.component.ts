import { Subscription } from 'rxjs';
import { Component, ElementRef, ViewChild, HostListener } from '@angular/core';
import { ActivatedRoute, Router, ParamMap } from '@angular/router';

import { Corpus, CorpusField, ResultOverview, QueryModel, User } from '../models/index';
import { CorpusService, DialogService, } from '../services/index';
import { ParamDirective } from '../param/param-directive';
import { AuthService } from '../services/auth.service';
import * as _ from 'lodash';
import { paramsHaveChanged } from '../utils/params';

@Component({
    selector: 'ia-search',
    templateUrl: './search.component.html',
    styleUrls: ['./search.component.scss'],
})
export class SearchComponent extends ParamDirective {
    @ViewChild('searchSection', { static: false })
    public searchSection: ElementRef;

    public isScrolledDown: boolean;

    public corpus: Corpus;

    /**
     * The filters have been modified.
     */
    public isSearching: boolean;
    public hasSearched: boolean;
    /**
     * Whether the total number of hits exceeds the download limit.
     */
    public hasLimitedResults = false;

    public user: User;
    protected corpusSubscription: Subscription;

    public queryModel: QueryModel;
    /**
     * This is the query text currently entered in the interface.
     */
    public queryText: string;

    public resultsCount = 0;
    public tabIndex: number;

    public filterFields: CorpusField[] = [];

    public showVisualization: boolean;

    constructor(
        private authService: AuthService,
        private corpusService: CorpusService,
        private dialogService: DialogService,
        route: ActivatedRoute,
        router: Router
    ) {
        super(route, router);
    }

    async initialize(): Promise<void> {
        this.tabIndex = 0;
        this.user = await this.authService.getCurrentUserPromise();
        this.corpusSubscription = this.corpusService.currentCorpus
            .filter((corpus) => !!corpus).subscribe((corpus) => {
            this.setCorpus(corpus);
        });
    }

    teardown() {
        this.user = undefined;
        this.corpusSubscription.unsubscribe();
    }

    setStateFromParams(params: ParamMap) {
        this.tabIndex = params.has('visualize') ? 1 : 0;
        this.showVisualization = params.has('visualize') ? true : false;
        if (paramsHaveChanged(this.queryModel, params)) {
            this.setQueryModel(false);
        }
    }

    @HostListener('window:scroll', [])
    onWindowScroll() {
        // mark that the search results have been scrolled down and we should some border
        this.isScrolledDown =
            this.searchSection.nativeElement.getBoundingClientRect().y === 0;
    }

    /**
     * Event triggered from search-results.component
     *
     * @param input
     */
    public onSearched(input: ResultOverview) {
        this.isSearching = false;
        this.hasSearched = true;
        this.resultsCount = input.resultsCount;
        this.hasLimitedResults = this.user.downloadLimit && input.resultsCount > this.user.downloadLimit;
        if (this.showVisualization) {
            this.tabIndex = 1;
        }
    }

    public showQueryDocumentation() {
        this.dialogService.showManualPage('query');
    }

    public showCorpusInfo(corpus: Corpus) {
        this.dialogService.showDescriptionPage(corpus);
    }

    public switchTabs(index: number) {
        this.tabIndex = index;
    }

    public search() {
        this.queryModel.setQueryText(this.queryText);
    }

    /**
     * Escape field names these so they won't interfere with any other parameter (e.g. query)
     */

    private setCorpus(corpus: Corpus) {
        if (!this.corpus || this.corpus.name !== corpus.name) {
            const reset = !_.isUndefined(this.corpus);
            this.corpus = corpus;
            this.setQueryModel(reset);
        }
    }

    private setQueryModel(reset: boolean) {
        const params = reset ? undefined : this.route.snapshot.queryParamMap;
        const queryModel = new QueryModel(this.corpus, params);
        this.queryModel = queryModel;
        this.queryText = queryModel.queryText;
        this.queryModel.update.subscribe(() => {
            this.queryText = this.queryModel.queryText;
            this.setParams(this.queryModel.toRouteParam());
        });
    }
}
