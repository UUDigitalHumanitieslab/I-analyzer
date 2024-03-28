import { Component, ElementRef, HostListener, ViewChild } from '@angular/core';
import { ActivatedRoute, ParamMap, Router } from '@angular/router';
import * as _ from 'lodash';
import { Subscription } from 'rxjs';

import { Corpus, CorpusField, ResultOverview, QueryModel, User } from '../models/index';
import { CorpusService, DialogService, ParamService, } from '../services/index';
import { ParamDirective } from '../param/param-directive';
import { AuthService } from '../services/auth.service';
import { distinct, filter } from 'rxjs/operators';
import { actionIcons, searchIcons } from '../shared/icons';
import { RouterStoreService } from '../store/router-store.service';

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

    searchIcons = searchIcons;
    actionIcons = actionIcons;

    activeTab: string;

    public queryModel: QueryModel;
    /**
     * This is the query text currently entered in the interface.
     */
    public queryText: string;

    resultOverview: ResultOverview;

    public filterFields: CorpusField[] = [];

    public showVisualization: boolean;

    public nullableParameters = [];

    protected corpusSubscription: Subscription;

    /**
     * This is a constant used to ensure that, when we are displayed in an iframe,
     * the filters are displayed even if there are no results.
     */
    private minIframeHeight = 1300;

    constructor(
        private authService: AuthService,
        private corpusService: CorpusService,
        private dialogService: DialogService,
        paramService: ParamService,
        route: ActivatedRoute,
        router: Router,
        private routerStoreService: RouterStoreService,
    ) {
        super(route, router, paramService);
    }

    @HostListener('window:scroll', [])
    onWindowScroll() {
        // mark that the search results have been scrolled down and we should some border
        this.isScrolledDown =
            this.searchSection.nativeElement.getBoundingClientRect().y === 0;
    }

    async initialize(): Promise<void> {
        this.user = await this.authService.getCurrentUserPromise();
        this.corpusSubscription = this.corpusService.currentCorpus
            .pipe(
                filter((corpus) => !!corpus),
                distinct(corpus => corpus.name),
            )
            .subscribe((corpus) => {
                this.setCorpus(corpus);
            });

        if (window.parent) {
            // iframe support
            window.parent.postMessage(['setHeight', this.minIframeHeight], '*');
        }
    }

    teardown() {
        this.user = undefined;
        this.corpusSubscription.unsubscribe();
        this.queryModel.complete();
    }

    setStateFromParams(params: ParamMap) {
        this.showVisualization = params.has('visualize') ? true : false;
    }

    /**
     * Event triggered from search-results.component
     *
     * @param input
     */
    public onSearched(input: ResultOverview) {
        this.isSearching = false;
        this.hasSearched = true;
        this.resultOverview = input;
        this.hasLimitedResults =
            this.user.downloadLimit &&
            input.resultsCount > this.user.downloadLimit;
    }

    public showQueryDocumentation() {
        this.dialogService.showManualPage('query');
    }

    public search() {
        this.queryModel.setQueryText(this.queryText);
    }

    private setCorpus(corpus: Corpus) {
        this.corpus = corpus;
        this.setQueryModel();
    }

    private setQueryModel() {
        if (this.queryModel) {
            this.queryModel.complete();
        }
        this.queryModel = new QueryModel(this.corpus, this.user !== null, this.routerStoreService);
        this.queryText = this.queryModel.queryText;
    }
}
