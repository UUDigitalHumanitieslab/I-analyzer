import { Input, Component, OnInit, OnChanges, OnDestroy, SimpleChanges } from '@angular/core';
import { Subscription } from 'rxjs';
import { SelectItem, SelectItemGroup } from 'primeng/api';
import * as _ from "lodash";

import { Corpus, CorpusField, AggregateResult, SearchResults } from '../models/index';
import { SearchService, DataService } from '../services/index';

@Component({
    selector: 'ia-visualization',
    templateUrl: './visualization.component.html',
    styleUrls: ['./visualization.component.scss'],
})

export class VisualizationComponent implements OnInit, OnChanges, OnDestroy {
    @Input() public corpus: Corpus;

    public visualizedFields: CorpusField[];

    public asPercentage: boolean;

    public showTableButtons: boolean;

    public visualizedField: CorpusField;

    public noResults: string = "Did not find data to visualize."
    public foundNoVisualsMessage: string = this.noResults;
    public errorMessage: string = '';
    public noVisualizations: boolean;

    public visDropdown: SelectItem[];
    public groupedVisualizations: SelectItemGroup[];
    public visualizationType: string;
    public freqtable: boolean = false;

    public aggResults: AggregateResult[];
    public relatedWordsGraph: {
        labels: string[],
        datasets: {
            label: string, data: number[]
        }[]
    };
    public relatedWordsTable: {
        [word: string]: number
    }
    public searchResults: SearchResults;

    // aggregate search expects a size argument
    public defaultSize: number = 10000;

    public subscription: Subscription;

    constructor(private searchService: SearchService, private dataService: DataService) {
    }

    ngOnChanges(changes: SimpleChanges) {
        if (changes['corpus']){
            this.visualizedFields = this.corpus && this.corpus.fields ?
            this.corpus.fields.filter(field => field.visualizationType != undefined) : [];
            this.visDropdown = this.visualizedFields.map(field => ({
                label: field.displayName,
                value: field.name
            }))
            if (this.corpus.word_models_present == true) {
                this.visDropdown.push({
                    label: 'Related Words',
                    value: 'relatedwords'
                })
            }
            if (this.visualizedFields === undefined) {
                this.noVisualizations = true;
            }
            else {
                this.noVisualizations = false;
                this.visualizedField = _.cloneDeep(this.visualizedFields[0]);
            }   
        }
    }

    ngOnInit() {
        this.subscription = this.dataService.searchResults$.subscribe(results => {
            if (results.total > 0) {
                this.searchResults = results;
                this.setVisualizedField(this.visualizedField.name);
            }
            else {
                this.aggResults = [];
            }
        });
        this.showTableButtons = true;
    }

    ngOnDestroy() {
        this.subscription.unsubscribe();
    }

    setVisualizedField(selectedField: string) {
        this.aggResults = [];
        this.errorMessage = '';
        if (selectedField == 'relatedwords') {
            this.visualizedField.visualizationType = selectedField;
            this.visualizedField.name = selectedField;
            this.visualizedField.displayName = 'Related Words';
            this.visualizedField.visualizationSort = 'similarity';
        }
        else {
            this.visualizedField = _.cloneDeep(this.visualizedFields.find(field => field.name === selectedField));
        }
        this.foundNoVisualsMessage = "Retrieving data..."
        if (this.visualizedField.visualizationType === 'wordcloud') {
            let queryModel = this.searchResults.queryModel;
            if (queryModel) {
                this.searchService.getWordcloudData(this.visualizedField.name, queryModel).then(result => {
                    // slice is used so the child component fires OnChange
                    this.aggResults = result[this.visualizedField.name];
                })
                    .catch(error => {
                        this.foundNoVisualsMessage = this.noResults;
                        this.errorMessage = error['message'];
                    });
            }
        }
        else if (this.visualizedField.visualizationType === 'timeline') {
            let aggregator = [{ name: this.visualizedField.name, size: this.defaultSize }];
            this.searchService.aggregateSearch(this.corpus, this.searchResults.queryModel, aggregator).then(visual => {
                this.aggResults = visual.aggregations[this.visualizedField.name];
            });
        }
        else if (this.visualizedField.visualizationType === 'relatedwords') {
            this.searchService.getRelatedWords(this.searchResults.queryModel.queryText, this.corpus.name).then(results => {
                this.relatedWordsGraph = results['graphData'];
                this.relatedWordsTable = results['tableData'];
            })
                .catch(error => {
                    this.relatedWordsGraph = undefined;
                    this.relatedWordsTable = undefined;
                    this.foundNoVisualsMessage = this.noResults;
                    console.log(error['message']);
                    this.errorMessage = error['message'];
                });
        }
        else {
            let aggregator = {name: this.visualizedField.name, size: this.defaultSize};
            this.searchService.aggregateSearch(this.corpus, this.searchResults.queryModel, [aggregator]).then(visual => {
                this.aggResults = visual.aggregations[this.visualizedField.name];
            });
        }
    }

    setErrorMessage(message: string) {
        this.searchResults = null;
        this.foundNoVisualsMessage = this.noResults;
        this.errorMessage = message;
    }

    showTable() {
        this.freqtable = true;
    }

    showChart() {
        this.freqtable = false;
    }
}
