import { HttpErrorResponse } from '@angular/common/http';
import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { APIEditableCorpus, CorpusDefinition } from '@models/corpus-definition';
import { ApiService } from '@services';
import { actionIcons, formIcons } from '@shared/icons';
import { Subject } from 'rxjs';
import { SlugifyPipe } from '../../shared/pipes/slugify.pipe';

@Component({
    selector: 'ia-create-definition',
    templateUrl: './create-definition.component.html',
    styleUrls: ['./create-definition.component.scss'],
})
export class CreateDefinitionComponent {
    actionIcons = actionIcons;
    formIcons = formIcons;

    corpus: CorpusDefinition;

    error: Error;

    reset$ = new Subject<void>();

    newCorpusTitle: string;

    constructor(
        private apiService: ApiService,
        private router: Router,
        private slugify: SlugifyPipe
    ) {
        this.corpus = new CorpusDefinition(this.apiService);
    }

    onJSONUpload(data: any) {
        this.corpus.setFromDefinition(data);
    }

    submit() {
        this.corpus.definition = {
            name: this.slugify.transform(this.newCorpusTitle),
            meta: {
                title: this.newCorpusTitle,
                languages: [],
            },
            fields: [],
            source_data: {
                type: 'csv',
            },
        };
        this.corpus.definition.meta.title = this.newCorpusTitle;
        this.saveCorpus();
    }

    saveCorpus(asImport: boolean = false) {
        this.error = undefined;
        this.corpus.save().subscribe({
            next: (result: APIEditableCorpus) => {
                const nextRoute = asImport
                    ? ['/corpus-definitions']
                    : ['/corpus-definitions', 'form', result.id];
                this.router.navigate(nextRoute);
            },
            error: (err: HttpErrorResponse) => {
                this.error = err;
            },
        });
    }
}
