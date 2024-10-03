import { Component } from '@angular/core';
import { APIEditableCorpus } from '@models/corpus-definition';
import { ApiService } from '@services';
import { actionIcons, documentIcons } from '@shared/icons';
import { Observable } from 'rxjs';

@Component({
    selector: 'ia-definitions-overview',
    templateUrl: './definitions-overview.component.html',
    styleUrls: ['./definitions-overview.component.scss'],
})
export class DefinitionsOverviewComponent {
    actionIcons = actionIcons;
    documentIcons = documentIcons;

    corpora$: Observable<APIEditableCorpus[]>;

    constructor(private apiService: ApiService) {
        this.corpora$ = this.apiService.corpusDefinitions();
    }

    delete(corpus: APIEditableCorpus) {
        this.apiService.deleteCorpus(corpus.id).subscribe(() => {
            this.corpora$ = this.apiService.corpusDefinitions();
        });
    }
}
