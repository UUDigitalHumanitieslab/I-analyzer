import { Component, Input, OnInit, OnDestroy } from '@angular/core';
import { Title } from '@angular/platform-browser';
import { ActivatedRoute } from '@angular/router';

import { Subscription }   from 'rxjs/Subscription';

import { Corpus, SearchFilterData, SearchSample } from '../models/index';
import { CorpusService, SearchService } from '../services/index';
@Component({
    selector: 'app-search',
    templateUrl: './search.component.html',
    styleUrls: ['./search.component.scss']
})
export class SearchComponent implements OnInit, OnDestroy {
    @Input() private searchData: Array<any>;

    public visibleTab: Tab;
    public corpus: Corpus;
    public availableCorpora: Promise<Corpus[]>;

    public isSearching: boolean;
    public searched: boolean;
    public query: string;
    public queryField: { [name: string]: { useAsFilter: boolean, visible: boolean, data?: SearchFilterData } };
    public sample: SearchSample;

    private searchResults: Array<any>;

    private subscription: Subscription;

    constructor(private corpusService: CorpusService, private searchService: SearchService, private activatedRoute: ActivatedRoute, private title: Title) {
        // listen to changes in the results returned by the searchService
        this.subscription = searchService.results$.subscribe(searchResults => { 
          this.searchResults = searchResults;
        });
        this.visibleTab = "search";
    }

    ngOnInit() {
        this.availableCorpora = this.corpusService.get();

        this.activatedRoute.params.subscribe(params => {
            let corpusName = params['corpus'];
            this.availableCorpora.then(items => {
                let found = items.find(corpus => corpus.name == corpusName);
                if (!found) {
                    throw 'Invalid corpus specified!';
                }
                this.corpus = found;
                this.title.setTitle(this.corpus.name);
                this.queryField = {};
                for (let field of this.corpus.fields) {
                    this.queryField[field.name] = { useAsFilter: false, visible: true };
                }
            });
        })
    }

    ngOnDestroy() {
        this.subscription.unsubscribe();
    }

    public enableFilter(name: string) {
        if (!this.queryField[name].useAsFilter) {
            this.queryField[name].useAsFilter = true;
        }
    }

    public showTab(tab: Tab) {
        this.visibleTab = tab;
    }

    public search() {
        this.isSearching = true;
        this.searchService.search(
            this.corpus.name,
            this.query,
            this.getQueryFields(),
            this.getFilterData())
            .then(sample => {
                this.sample = sample;
                this.isSearching = false;
                this.searched = true;
            });
    }

    public visualize() {
        this.searchService.searchForVisualization(
            this.corpus.name,
            this.query,
            this.getQueryFields(),
            this.getFilterData())
    }

    public download() {
        this.searchService.searchAsCsv(
            this.corpus.name,
            this.query,
            this.getQueryFields(),
            this.getFilterData());
    }

    public updateFilterData(name: string, data: any) {
        this.queryField[name].data = data;
    }

    private getQueryFields(): string[] {
        return Object.keys(this.queryField).filter(field => this.queryField[field].visible);
    }
    private getFilterData(): SearchFilterData[] {
        let data = [];
        for (let fieldName of Object.keys(this.queryField)) {
            let field = this.queryField[fieldName];
            if (field.useAsFilter) {
                data.push(field.data);
            }
        }
        return data;
    }
}

type Tab = "search" | "columns";
