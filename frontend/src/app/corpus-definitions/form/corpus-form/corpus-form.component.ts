import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { CorpusDefinition } from '../../../models/corpus-definition';
import { ApiService } from '../../../services';
import { MenuItem } from 'primeng/api';
import { CorpusDefinitionService } from '../../corpus-definition.service';
import { tap } from 'rxjs';
import { cloneDeep } from 'lodash';

@Component({
    selector: 'ia-corpus-form',
    templateUrl: './corpus-form.component.html',
    styleUrl: './corpus-form.component.scss',
    providers: [CorpusDefinitionService],
})
export class CorpusFormComponent {
    steps$ = this.corpusDefService.steps$.asObservable();
    activeStep$ = this.corpusDefService.activeStep$.asObservable();

    corpus$ = this.corpusDefService.corpus$.asObservable();

    constructor(
        private apiService: ApiService,
        private route: ActivatedRoute,
        private corpusDefService: CorpusDefinitionService
    ) {
        const id = parseInt(this.route.snapshot.params['corpusID'], 10);
        const fetchedCorpus = new CorpusDefinition(this.apiService, id);
        this.corpusDefService.setCorpus(fetchedCorpus);
    }

    onActiveIndexChange(event: number) {
        this.corpusDefService.activateStep(event);
    }
}
