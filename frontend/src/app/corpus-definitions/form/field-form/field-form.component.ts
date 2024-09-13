import { Component, Input, SimpleChanges } from '@angular/core';
import { FormArray, FormBuilder, FormControl, FormGroup } from '@angular/forms';
import {
    APICorpusDefinitionField,
    CorpusDefinition,
} from '@models/corpus-definition';
import { CorpusDefinitionService } from 'app/corpus-definitions/corpus-definition.service';
import { MenuItem } from 'primeng/api';
import { Subject, takeUntil } from 'rxjs';
import { ISO639Languages } from '../constants';

@Component({
    selector: 'ia-field-form',
    templateUrl: './field-form.component.html',
    styleUrl: './field-form.component.scss',
})
export class FieldFormComponent {
    @Input() corpus: CorpusDefinition;
    destroy$ = new Subject<void>();

    fieldsForm = new FormGroup({
        fields: new FormArray([]),
    });

    fieldTypeOptions: MenuItem[] = [
        { label: 'text (content)', value: 'text_content' },
        { label: 'text (metadata)', value: 'text_content' },
        { label: 'number (integer)', value: 'integer' },
        { label: 'number (decimal)', value: 'float' },
        { label: 'date', value: 'date' },
    ];

    languageOptions = ISO639Languages;

    constructor(
        private formBuilder: FormBuilder,
        private corpusDefService: CorpusDefinitionService
    ) {}

    get fields(): FormArray {
        return this.fieldsForm.get('fields') as FormArray;
    }

    makeFieldFormgroup(field: APICorpusDefinitionField): FormGroup {
        let fg = new FormGroup({
            display_name: new FormControl(),
            description: new FormControl(),
            type: new FormControl(),
            options: new FormGroup({
                search: new FormControl(),
                filter: new FormControl(),
                preview: new FormControl(),
                visualize: new FormControl(),
                sort: new FormControl(),
                hidden: new FormControl(),
            }),
            language: new FormControl(),
        });

        fg.patchValue(field);

        return fg;
    }

    ngOnChanges(changes: SimpleChanges): void {
        console.log(this.fieldTypeOptions);
        if (changes.corpus) {
            this.corpus.definitionUpdated$
                .pipe(takeUntil(this.destroy$))
                .subscribe(
                    () =>
                        // this.fieldForm.patchValue(this.corpus.definition.meta)
                        (this.fieldsForm.controls.fields = new FormArray(
                            this.corpus.definition.fields.map(
                                this.makeFieldFormgroup
                            )
                        ))
                );
        }
    }

    ngOnDestroy(): void {
        this.destroy$.next();
        this.destroy$.complete();
    }

    onSubmit(): void {
        const newFields = this.fields as unknown as APICorpusDefinitionField[];
        this.corpus.definition.fields =
            newFields as CorpusDefinition['definition']['fields'];
        this.corpus.save().subscribe({
            next: console.log,
            error: console.error,
        });
    }
}
