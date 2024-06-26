/* eslint-disable @typescript-eslint/member-ordering */
import {
    Component,
    ElementRef,
    EventEmitter,
    HostListener,
    Input,
    OnChanges,
    OnDestroy,
    Output,
    SimpleChanges,
    ViewChild,
} from '@angular/core';

import { Observable, Subject } from 'rxjs';
import { map, takeUntil } from 'rxjs/operators';
import { ShowError } from '../error/error.component';
import {
    QueryModel,
    ResultOverview,
    SearchResults,
    User,
} from '../models/index';
import { PageResults, PageResultsParameters } from '../models/page-results';
import { SearchService } from '../services';
import { RouterStoreService } from '../store/router-store.service';

const MAXIMUM_DISPLAYED = 10000;

@Component({
    selector: 'ia-search-results',
    templateUrl: './search-results.component.html',
    styleUrls: ['./search-results.component.scss'],
})
export class SearchResultsComponent implements OnChanges, OnDestroy {
    @ViewChild('resultsNavigation', { static: true })
    public resultsNavigation: ElementRef;

    /**
     * The search queryModel to use
     */
    @Input()
    public queryModel: QueryModel;

    @Input()
    public user: User;

    @Output()
    public searched = new EventEmitter<ResultOverview>();

    public pageResults: PageResults;

    public isLoading = false;
    public isScrolledDown: boolean;

    public results: SearchResults;

    public resultsPerPage = 20;

    public imgSrc: Uint8Array;

    error$: Observable<ShowError>;

    /** tab on which the focused document should be opened */
    public documentTabIndex: number;

    private destroy$ = new Subject<void>();

    constructor(
        private routerStoreService: RouterStoreService,
        private searchService: SearchService,
    ) {}

    ngOnChanges(changes: SimpleChanges) {
        if (changes.queryModel) {
            this.pageResults?.complete();
            this.pageResults = new PageResults(
                this.routerStoreService,
                this.searchService,
                this.queryModel
            );
            this.error$ = this.pageResults.error$.pipe(map(this.parseError));
            this.pageResults.result$
                .pipe(takeUntil(this.destroy$))
                .subscribe((result) => {
                    this.searched.emit({
                        queryText: this.queryModel.queryText,
                        sort: this.pageResults.state$.value.sort,
                        highlight: this.pageResults.state$.value.highlight,
                        resultsCount: result?.total,
                    });
                });
        }
    }

    ngOnDestroy(): void {
        this.pageResults?.complete();
        this.destroy$.next(undefined);
        this.destroy$.complete();
    }

    setParameters(parameters: PageResultsParameters) {
        this.pageResults?.setParams(parameters);
    }

    totalDisplayed(totalResults: number) {
        return Math.min(totalResults, MAXIMUM_DISPLAYED);
    }

    @HostListener('window:scroll', [])
    onWindowScroll() {
        // mark that the search results were scrolled down beyond 68 pixels from top (position underneath sticky search bar)
        // this introduces a box shadow
        if (this.resultsNavigation !== undefined) {
            this.isScrolledDown =
                this.resultsNavigation.nativeElement.getBoundingClientRect()
                    .y === 68;
        }
    }

    private parseError(error): ShowError {
        if (error) {
            return {
                date: new Date().toISOString(),
                href: location.href,
                message: error.message || 'An unknown error occurred',
            };
        }
    }
}
