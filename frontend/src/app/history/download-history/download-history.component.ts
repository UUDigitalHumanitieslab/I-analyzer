import { Component, OnDestroy, OnInit } from '@angular/core';
import { faDownload, faTrash } from '@fortawesome/free-solid-svg-icons';
import * as _ from 'lodash';
import { Subject } from 'rxjs';
import { concatMap, takeUntil, tap } from 'rxjs/operators';
import {
    Download,
    DownloadOptions,
    DownloadParameters,
    DownloadType,
    QueryModel,
} from '../../models';
import {
    ApiService,
    CorpusService,
    DownloadService,
    NotificationService,
} from '../../services';
import { esQueryToQueryModel } from '../../utils/es-query';
import { findByName } from '../../utils/utils';
import { HistoryDirective } from '../history.directive';

@Component({
    selector: 'ia-download-history',
    templateUrl: './download-history.component.html',
    styleUrls: ['./download-history.component.scss']
})
export class DownloadHistoryComponent extends HistoryDirective implements OnDestroy, OnInit {
    downloads: Download[];

    faDownload = faDownload;
    faTrash = faTrash;

    itemToDownload: Download;

    destroy$ = new Subject();

    constructor(
        private downloadService: DownloadService,
        private apiService: ApiService,
        corpusService: CorpusService,
        private notificationService: NotificationService
    ) {
        super(corpusService);
    }

    ngOnInit(): void {
        this.retrieveCorpora();
        this.refreshDownloads();
    }

    ngOnDestroy(): void {
        this.destroy$.next();
        this.destroy$.complete();
    }

    refreshDownloads() {
        this.apiService.downloads()
            .then(downloadHistory => this.downloads = this.sortByDate(downloadHistory))
            .catch(err => console.error(err));
    }

    downloadType(type: DownloadType): string {
        const displayNames = {
            search_results: 'Search results',
            date_term_frequency: 'Term frequency',
            aggregate_term_frequency: 'Term frequency',
            ngram: 'Neighbouring words'
            // timeline/histogram distinction is relevant for backend but not for the user
        };
        return displayNames[type];
    }

    queryText(download: Download): string {
        const queryModels = this.getAllQueryModels(download);
        const queryTexts = queryModels.map(model => model.queryText);
        return _.join(queryTexts, ', ');
    }

    getAllQueryModels(download: Download): QueryModel[] {
        const esQueries =  'es_query' in download.parameters ?
            [download.parameters.es_query] : download.parameters.map(p => p.es_query);
        const corpus = findByName(this.corpora, download.corpus);
        return esQueries.map(esQuery => esQueryToQueryModel(esQuery, corpus));
    }


    getQueryModel(download: Download): QueryModel {
        const queryModels = this.getAllQueryModels(download);
        return queryModels[0];
    }

    getFields(download: Download): string {
        const parameters: DownloadParameters = download.parameters;
        const fieldNames =  'fields' in parameters ?
            parameters.fields : [parameters[0].field_name];
        const corpus = findByName(this.corpora, download.corpus);
        const fields = fieldNames.map(fieldName =>
            findByName(corpus.fields, fieldName).displayName
        );
        return _.join(fields, ', ');
    }

    downloadFile(download: Download, options: DownloadOptions) {
        this.downloadService.retrieveFinishedDownload(download.id, options).then( result => {
            if (result.status === 200) {
                saveAs(result.body, download.filename);
                this.itemToDownload = undefined;
            } else {
                this.downloadFailed(result);
            }
        }).catch(this.downloadFailed.bind(this));
    }

    downloadFailed(result): void {
        console.error(result);
        this.notificationService.showMessage('could not download file', 'danger');
        this.itemToDownload = undefined;
    }

    public deleteDownload(download: Download): void {
        this.downloadService
            .deleteDownload(download.id)
            .pipe(
                takeUntil(this.destroy$),
                tap(() => this.refreshDownloads())
                )
            .subscribe(
                res => this.deleteSuccess(),
                err => this.deleteFailure(err)
            );
    }

    public deleteAllDownloads(): void {
        this.downloadService
            .deleteAll()
            .pipe(
                takeUntil(this.destroy$),
                tap(() => this.refreshDownloads())
            )
            .subscribe(
                (res) => this.deleteSuccess(res),
                (err) => this.deleteFailure(err)
            );
    }

    private deleteSuccess = (msg?: string): void => {
        this.notificationService.showMessage(msg || 'deleted download', 'success');
    };


    private deleteFailure = (err: any): void => {
        console.error(err);
        this.notificationService.showMessage('failed to delete file', 'danger');
    };

}
