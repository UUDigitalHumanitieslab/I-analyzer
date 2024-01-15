import { Injectable } from '@angular/core';

import { saveAs } from 'file-saver';
import * as _ from 'lodash';
import { Observable } from 'rxjs';
import { Corpus, CorpusField, Download, DownloadOptions, QueryModel } from '../models/index';
import { ApiService } from './api.service';
import { ElasticSearchService } from './elastic-search.service';

@Injectable()
export class DownloadService {
    constructor(
        private apiService: ApiService,
        private elasticSearchService: ElasticSearchService
    ) {}

    /**
     * download csv directly via api service.
     */
    public async download(
        corpus: Corpus,
        queryModel: QueryModel,
        fields: CorpusField[],
        requestedResults: number,
        route: string,
        highlightFragmentSize: number,
        fileOptions: DownloadOptions
    ): Promise<string | void> {
        const esQuery = queryModel.toEsQuery(); // to create elastic search query
        const parameters = _.merge(
            {
                corpus: corpus.name,
                es_query: esQuery,
                fields: fields.map((field) => field.name),
                size: requestedResults,
                route,
            },
            fileOptions
        );
        return this.apiService
            .download(parameters)
            .then((result) => {
                if (result.status === 200) {
                    const filename = this.getFileNameFromHttpResponse(result);
                    saveAs(result.body, filename);
                    return 'success';
                }
            })
            .catch((error) => {
                throw new Error(error.headers.message[0]);
            });
    }

    public async downloadTask(
        corpus: Corpus,
        queryModel: QueryModel,
        fields: CorpusField[],
        route: string,
        highlightFragmentSize: number
    ) {
        /**
         * Downloads the given tabular data as a CSV file on the backend.
         * Link to CSV is sent to user per email
         *
         * @param corpus Corpus to be queried for constructing the file.
         * @param queryModel QueryModel for which download is requested.
         * @param fields The fields to appear as columns in the csv.
         */
        const esQuery = queryModel.toEsQuery(); // to create elastic search query
        return this.apiService
            .downloadTask({
                corpus: corpus.name,
                es_query: esQuery,
                fields: fields.map((field) => field.name),
                route,
            })
            .then((result) => result)
            .catch((error) => {
                throw new Error(error.headers.message[0]);
            });
    }

    public retrieveFinishedDownload(id: number, options: DownloadOptions) {
        const parameters = _.merge({ id }, options);
        return this.apiService.csv(parameters);
    }

    public deleteDownload(id: number): Observable<Download> {
        return this.apiService.deleteDownload(id);
    }

    public deleteAll(): Observable<string> {
        return this.apiService.deleteAllDownloads();
    }
    private getFileNameFromHttpResponse = (httpResponse) => {
        const contentDispositionHeader = httpResponse.headers.get(
            'Content-Disposition'
        );
        const result = contentDispositionHeader
            .split(';')[1]
            .trim()
            .split('=')[1];
        return result.replace(/"/g, '');
    };
}
