import { Component, OnDestroy, OnInit } from '@angular/core';
import { Corpus } from '@models';
import { CorpusDataFile, DataFileInfo } from '@models/corpus-definition';
import { ApiService } from '@services';
import { actionIcons, formIcons } from '@shared/icons';
import { CorpusDefinitionService } from 'app/corpus-definitions/corpus-definition.service';
import * as _ from 'lodash';
import {
    BehaviorSubject,
    distinctUntilChanged,
    filter,
    map,
    of,
    Subject,
    switchMap,
    takeUntil,
} from 'rxjs';

@Component({
    selector: 'ia-upload-sample',
    templateUrl: './upload-sample.component.html',
    styleUrl: './upload-sample.component.scss',
})
export class UploadSampleComponent implements OnInit, OnDestroy {
    actionIcons = actionIcons;
    formIcons = formIcons;

    file$ = new BehaviorSubject<File | undefined>(undefined);
    dataFile: CorpusDataFile;
    fileInfo$ = new Subject<DataFileInfo>();
    error$ = new BehaviorSubject<Error | undefined>(undefined);
    destroy$ = new Subject<void>();

    delimiterOptions = [
        { label: ', comma', value: ',' },
        { label: '; semicolon', value: ';' },
        { label: 'tab', value: '\t' },
    ];

    constructor(
        private apiService: ApiService,
        private corpusDefService: CorpusDefinitionService
    ) {}

    ngOnInit() {
        this.apiService
            .listDataFiles(this.corpusDefService.corpus$.value.id, true)
            .pipe(
                map(_.head),
                filter(_.negate(_.isUndefined)),
                switchMap((dataFile: CorpusDataFile) => {
                    this.dataFile = dataFile;
                    return this.apiService.getDataFileInfo(dataFile);
                })
            )
            .subscribe({
                next: (info) => {
                    this.fileInfo$.next(info);
                },
                error: (err) => this.error$.next(err),
            });

        this.fileInfo$
            .pipe(
                takeUntil(this.destroy$),
                distinctUntilChanged(_.isEqual),
                switchMap((info: DataFileInfo) => {
                    const fields = _.map(info, (dtype, colName) =>
                        this.corpusDefService.makeDefaultField(dtype, colName)
                    );
                    return of(fields);
                })
            )
            .subscribe({
                next: (fields) => this.corpusDefService.setFields(fields),
                error: console.error,
            });
    }

    onDelimiterChange(event: InputEvent) {
        this.corpusDefService.setDelimiter(event.target['value']);
    }

    onUpload(event: InputEvent) {
        const files: File[] = event.target['files'];
        const file = files ? _.first(files) : undefined;
        this.file$.next(file);
        const corpusId = this.corpusDefService.corpus$.value.id;
        this.apiService
            .createDataFile(corpusId, file)
            .pipe(
                takeUntil(this.destroy$),
                switchMap((dataFile) => {
                    this.dataFile = dataFile;
                    return this.apiService.getDataFileInfo(dataFile);
                })
            )
            .subscribe({
                next: (info) => {
                    this.fileInfo$.next(info);
                },
                error: (err) => this.error$.next(err),
            });
    }

    onSubmit() {
        this.corpusDefService.toggleStep(2);
        this.corpusDefService.activateStep(2);
    }

    resetFields() {
        this.apiService.deleteDataFile(this.dataFile).subscribe({
            next: () => {
                this.corpusDefService.setFields([]);
                this.fileInfo$.next(undefined);
            },
            error: console.error,
        });
    }

    ngOnDestroy(): void {
        this.destroy$.next();
        this.destroy$.complete();
    }
}
