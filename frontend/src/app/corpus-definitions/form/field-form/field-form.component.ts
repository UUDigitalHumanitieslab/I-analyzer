import { Component, Input, SimpleChanges } from '@angular/core';
import { FormArray, FormControl, FormGroup } from '@angular/forms';
import {
    APICorpusDefinitionField,
    CorpusDefinition,
} from '@models/corpus-definition';
import { MenuItem } from 'primeng/api';
import { Subject, takeUntil } from 'rxjs';
import { ISO639Languages } from '../constants';
import * as _ from 'lodash';

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
        {
            label: 'text (content)',
            value: 'text_content',
            helpText:
                'Main document text. Can consist of multiple paragraphs. Can be used to search.',
            hasLanguage: true,
        },
        {
            label: 'text (metadata)',
            value: 'text_metadata',
            helpText:
                'Metadata text. Limited to a single paragraph. Can be used to filter and/or search.',
            hasLanguage: true,
        },
        { label: 'number (integer)', value: 'integer' },
        { label: 'number (decimal)', value: 'float' },
        { label: 'date', value: 'date' },
        {
            label: 'boolean',
            value: 'boolean',
            helpText: 'True/false field. Can be used to filter.',
        },
    ];

    languageOptions = ISO639Languages;

    constructor() {}

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
            // hidden in the form, but included to ease syncing model with form
            name: new FormControl(),
            extract: new FormGroup({
                column: new FormControl(),
            }),
        });
        fg.patchValue(field);

        return fg;
    }

    getFieldProperty(field: FormGroup, prop: string) {
        const fieldType = field.get('type').value;
        const option = _.find(this.fieldTypeOptions, { value: fieldType });
        return option[prop];
    }

    ngOnChanges(changes: SimpleChanges): void {
        if (changes.corpus) {
            this.corpus.definitionUpdated$
                .pipe(takeUntil(this.destroy$))
                .subscribe(
                    () =>
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
        const newFields = this.fields.value as APICorpusDefinitionField[];
        this.corpus.definition.fields =
            newFields as CorpusDefinition['definition']['fields'];
        this.corpus.save().subscribe({
            next: console.log,
            error: console.error,
        });
    }
}
