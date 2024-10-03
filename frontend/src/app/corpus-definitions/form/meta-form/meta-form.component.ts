import {
    Component,
    Input,
    OnChanges,
    OnDestroy,
    SimpleChanges,
} from '@angular/core';
import { FormBuilder } from '@angular/forms';
import { Subject, takeUntil } from 'rxjs';
import { CorpusDefinitionService } from '../../corpus-definition.service';
import { CorpusDefinition } from '../../../models/corpus-definition';

@Component({
    selector: 'ia-meta-form',
    templateUrl: './meta-form.component.html',
    styleUrl: './meta-form.component.scss',
})
export class MetaFormComponent implements OnChanges, OnDestroy {
    @Input() corpus: CorpusDefinition;

    categories = [
        { value: 'parliament', label: 'Parliamentary debates' },
        { value: 'periodical', label: 'Newspapers and other periodicals' },
        { value: 'finance', label: 'Financial reports' },
        { value: 'ruling', label: 'Court rulings' },
        { value: 'review', label: 'Online reviews' },
        { value: 'inscription', label: 'Funerary inscriptions' },
        { value: 'oration', label: 'Orations' },
        { value: 'book', label: 'Books' },
        { value: 'informative', label: 'Informative' },
        { value: undefined, label: 'Other' },
    ];

    metaForm = this.formBuilder.group({
        title: [''],
        description: [''],
        category: [''],
        date_range: this.formBuilder.group({
            min: [''],
            max: [''],
        }),
        languages: [['']],
    });

    destroy$ = new Subject<void>();

    constructor(
        private formBuilder: FormBuilder,
        private corpusDefService: CorpusDefinitionService
    ) {}

    ngOnChanges(changes: SimpleChanges): void {
        if (changes.corpus) {
            this.corpus.definitionUpdated$
                .pipe(takeUntil(this.destroy$))
                .subscribe(() =>
                    this.metaForm.patchValue(this.corpus.definition.meta)
                );
        }
    }

    ngOnDestroy(): void {
        this.destroy$.next();
        this.destroy$.complete();
    }

    onSubmit(): void {
        const newMeta = this.metaForm.value;
        this.corpus.definition.meta =
            newMeta as CorpusDefinition['definition']['meta'];
        this.corpus.save().subscribe({
            next: () => {
                this.corpusDefService.toggleStep(1);
                this.corpusDefService.activateStep(1);
            },
            error: console.error,
        });
    }
}
