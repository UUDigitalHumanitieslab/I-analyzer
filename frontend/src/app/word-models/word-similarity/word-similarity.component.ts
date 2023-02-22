import { Component, EventEmitter, Input, OnChanges, Output, SimpleChanges } from '@angular/core';
import * as _ from 'lodash';
import { Corpus, WordSimilarity } from '../../models';
import { ChartOptionsService, WordmodelsService } from '../../services';

@Component({
    selector: 'ia-word-similarity',
    templateUrl: './word-similarity.component.html',
    styleUrls: ['./word-similarity.component.scss']
})
export class WordSimilarityComponent implements OnChanges {
    @Input() queryText: string;
    @Input() corpus: Corpus;
    @Input() asTable: boolean;
    @Input() palette: string[];

    comparisonTermLimit = Infinity;
    comparisonTerms: string[] = [];

    @Output() error = new EventEmitter();
    @Output() isLoading = new EventEmitter<boolean>();

    results: WordSimilarity[][];
    timeIntervals: string[];

    data: WordSimilarity[];

    constructor(private wordModelsService: WordmodelsService,
        private chartOptionsService: ChartOptionsService) { }

    ngOnChanges(changes: SimpleChanges): void {
        if ((changes.queryText || changes.corpus) && this.comparisonTerms.length) {
            this.getData();
        } else {
            if (this.results) {
                this.onDataLoaded(this.results);
            }
        }
    }

    updateComparisonTerms(terms: string[] = []) {
        this.comparisonTerms = terms;
        this.getData();
    }

    get chartTitle() {
        return this.chartOptionsService.getChartHeader('Word similarity', this.corpus.name, this.queryText);
    }

    getData(): void {
        this.showLoading(
            Promise.all(this.comparisonTerms.map(term =>
                this.wordModelsService.getWordSimilarity(this.queryText, term, this.corpus.name)
            ))
        ).then(this.onDataLoaded.bind(this));
    }

    /** execute a process with loading spinner */
    async showLoading(promise): Promise<any> {
        this.isLoading.next(true);
        const result = await promise;
        this.isLoading.next(false);
        return result;
    }

    getTimePoints(points: WordSimilarity[]) {
        return points.map(point => point.time);
    }

    onDataLoaded(data: WordSimilarity[][]): void {
        this.results = data;
        this.timeIntervals = (data.length && data[0].length) ? this.getTimePoints(data[0]) : this.timeIntervals;
        this.data = _.flatten(this.results);
    }



    get tableFileName(): string {
        return `word similarity - ${this.queryText} - ${this.corpus?.title}`;
    }

}
