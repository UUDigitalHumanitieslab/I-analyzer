/* eslint-disable @typescript-eslint/member-ordering */
import { Injectable } from '@angular/core';

import { HttpClient, HttpParams } from '@angular/common/http';
import { interval, Observable } from 'rxjs';
import { filter, switchMap, take, takeUntil } from 'rxjs/operators';
import { ImageInfo } from '../image-view/image-view.component';
import {
    AggregateTermFrequencyParameters,
    Corpus,
    CorpusDocumentationPage,
    DateTermFrequencyParameters,
    DocumentTagsResponse,
    Download,
    DownloadOptions,
    FieldCoverage,
    FoundDocument,
    GeoDocument,
    GeoLocation,
    LimitedResultsDownloadParameters,
    MostFrequentWordsResult,
    NGramRequestParameters,
    QueryDb,
    ResultsDownloadParameters,
    Tag,
    TaskResult,
    TaskSuccess,
    TasksOutcome,
    UserResponse,
    UserRole,
    WordcloudParameters,
} from '@models';
import { environment } from '@environments/environment';
import * as _ from 'lodash';
import {
    APIEditableCorpus,
    CorpusDataFile,
    DataFileInfo,
} from '@models/corpus-definition';

interface SolisLoginResponse {
    success: boolean;
    id: number;
    username: string;
    role: UserRole;
    downloadLimit: number | null;
    queries: QueryDb[];
}

@Injectable({
    providedIn: 'root',
})
export class ApiService {
    private apiUrl = environment.apiUrl;

    private authApiUrl = 'users';
    private visApiURL = 'visualization';
    private downloadApiURL = 'download';
    private corpusApiUrl = 'corpus';
    private tagApiUrl = 'tag';

    private authApiRoute = (route: string): string =>
        `/${this.authApiUrl}/${route}/`;

    private apiRoute = (subApi: string, route: string): string =>
        `${this.apiUrl}/${subApi}/${route}`;

    constructor(private http: HttpClient) {}

    public deleteSearchHistory(): Observable<any> {
        return this.http.post('/api/search_history/delete_all/', {});
    }

    public searchHistory() {
        return this.http.get<QueryDb[]>('/api/search_history/').toPromise();
    }

    public downloads(): Promise<Download[]> {
        return this.http.get<Download[]>('/api/download/').toPromise();
    }

    // Media
    public getMedia(data: { args: string }): Promise<any> {
        const url = `/api/get_media${data.args}`;
        return this.http
            .get(url, { observe: 'response', responseType: 'arraybuffer' })
            .toPromise();
    }

    public requestMedia(data: {
        corpus: string;
        document: FoundDocument;
    }): Promise<{ media: string[]; info?: ImageInfo }> {
        const serializableDocument = _.pick(data.document, [
            'id',
            'fieldValues',
        ]);
        const requestData = {
            corpus: data.corpus,
            document: serializableDocument,
        };
        return this.http
            .post<{ media: string[]; info?: ImageInfo }>(
                '/api/request_media',
                requestData
            )
            .toPromise();
    }

    public downloadPdf(data: {
        corpus_index: string;
        filepath: string;
    }): Promise<any> {
        const url = `/api/download_pdf/${data.corpus_index}/${data.filepath}`;
        return this.http.get(url).toPromise();
    }

    // Tasks
    public getTasksStatus(tasks: TaskResult): Observable<TasksOutcome> {
        return this.http.post<TasksOutcome>('/api/task_status', tasks);
    }

    public abortTasks(data: TaskResult): Promise<TaskSuccess> {
        return this.http
            .post<TaskSuccess>('/api/abort_tasks', data)
            .toPromise();
    }

    private tasksDone(response: TasksOutcome) {
        return response.status === 'done';
    }

    public pollTasks(
        ids: string[],
        stopPolling$: Observable<void>
    ): Observable<TasksOutcome> {
        return interval(5000).pipe(
            takeUntil(stopPolling$),
            switchMap((arg) => this.getTasksStatus({ task_ids: ids })),
            filter(this.tasksDone),
            take(1)
        );
    }

    // Visualization
    public wordCloud(
        data: WordcloudParameters
    ): Observable<MostFrequentWordsResult[]> {
        const url = this.apiRoute(this.visApiURL, 'wordcloud');
        return this.http.post<MostFrequentWordsResult[]>(url, data);
    }

    public geoData(data: WordcloudParameters): Promise<GeoDocument[]> {
        const url = this.apiRoute(this.visApiURL, 'geo');
        return this.http.post<GeoDocument[]>(url, data).toPromise();
    }

    public geoCentroid(data: {corpus: string, field: string}): Promise<GeoLocation> {
        const url = this.apiRoute(this.visApiURL, 'geo_centroid');
        return this.http.post<GeoLocation>(url, data).toPromise();
    }

    public ngramTasks(data: NGramRequestParameters): Promise<TaskResult> {
        const url = this.apiRoute(this.visApiURL, 'ngram');
        return this.http.post<TaskResult>(url, data).toPromise();
    }

    public getAggregateTermFrequency(
        data: AggregateTermFrequencyParameters
    ): Promise<TaskResult> {
        const url = this.apiRoute(this.visApiURL, 'aggregate_term_frequency');
        return this.http.post<TaskResult>(url, data).toPromise();
    }

    public getDateTermFrequency(
        data: DateTermFrequencyParameters
    ): Promise<TaskResult> {
        const url = this.apiRoute(this.visApiURL, 'date_term_frequency');
        return this.http.post<TaskResult>(url, data).toPromise();
    }

    fieldCoverage(corpusName: string): Promise<FieldCoverage> {
        const url = this.apiRoute(this.visApiURL, `coverage/${corpusName}`);
        return this.http.get<FieldCoverage>(url).toPromise();
    }

    // Download
    public requestFullData(
        data:
            | {
                  visualization: 'date_term_frequency';
                  parameters: DateTermFrequencyParameters[];
                  corpus_name: string;
              }
            | {
                  visualization: 'aggregate_term_frequency';
                  parameters: AggregateTermFrequencyParameters[];
                  corpus_name: string;
              }
            | {
                  visualization: 'ngram';
                  parameters: NGramRequestParameters;
                  corpus_name: string;
              }
    ): Promise<TaskResult> {
        const url = this.apiRoute(this.downloadApiURL, 'full_data');
        return this.http.post<TaskResult>(url, data).toPromise();
    }

    public download(data: LimitedResultsDownloadParameters): Promise<any> {
        const url = this.apiRoute(this.downloadApiURL, 'search_results');
        return this.http
            .post<TaskResult>(url, data, {
                observe: 'response',
                responseType: 'blob' as 'json',
            })
            .toPromise();
    }

    public csv(
        data: { id: number } | ({ id: number } & DownloadOptions)
    ): Promise<any> {
        const url = this.apiRoute(this.downloadApiURL, `csv/${data.id}`);
        return this.http
            .get(url, {
                observe: 'response',
                responseType: 'blob' as 'json',
            })
            .toPromise();
    }

    public downloadTask(data: ResultsDownloadParameters): Promise<TaskResult> {
        const url = this.apiRoute(this.downloadApiURL, 'search_results_task');
        return this.http.post<TaskResult>(url, data).toPromise();
    }

    // Corpus
    public corpusDocumentationPages(
        corpus?: Corpus
    ): Observable<CorpusDocumentationPage[]> {
        const params = new URLSearchParams({ corpus: corpus.name }).toString();
        const url = this.apiRoute(
            this.corpusApiUrl,
            `documentation/?${params}`
        );
        return this.http.get<CorpusDocumentationPage[]>(url.toString());
    }

    public corpusDocumentationPage(
        pageID: number
    ): Observable<CorpusDocumentationPage> {
        const url = this.apiRoute(
            this.corpusApiUrl,
            `documentation/${pageID}/`
        );
        return this.http.get<CorpusDocumentationPage>(url);
    }

    public corpus() {
        return this.http.get<Corpus[]>('/api/corpus/');
    }

    // Corpus definitions

    public corpusDefinitions(): Observable<APIEditableCorpus[]> {
        return this.http.get<APIEditableCorpus[]>('/api/corpus/definitions/');
    }

    public corpusDefinition(corpusID: number): Observable<APIEditableCorpus> {
        return this.http.get<APIEditableCorpus>(
            `/api/corpus/definitions/${corpusID}/`
        );
    }

    public createCorpus(
        data: APIEditableCorpus
    ): Observable<APIEditableCorpus> {
        return this.http.post<APIEditableCorpus>(
            '/api/corpus/definitions/',
            data
        );
    }

    public updateCorpus(
        corpusID: number,
        data: APIEditableCorpus
    ): Observable<APIEditableCorpus> {
        return this.http.put<APIEditableCorpus>(
            `/api/corpus/definitions/${corpusID}/`,
            data
        );
    }

    public deleteCorpus(corpusID: number): Observable<any> {
        return this.http.delete(`/api/corpus/definitions/${corpusID}/`);
    }

    // Corpus datafiles
    public createDataFile(
        corpusId: number,
        file: File
    ): Observable<CorpusDataFile> {
        const formData: FormData = new FormData();
        formData.append('file', file, 'newFile.csv');
        formData.append('corpus', String(corpusId));
        formData.append('is_sample', 'True');
        return this.http.post<CorpusDataFile>(
            `/api/corpus/datafiles/`,
            formData
        );
    }

    public deleteDataFile(dataFile: CorpusDataFile): Observable<null> {
        const url = `/api/corpus/datafiles/${dataFile.id}/`;
        return this.http.delete<null>(url);
    }

    public listDataFiles(
        corpusId: number,
        samples: boolean = false
    ): Observable<CorpusDataFile[]> {
        const params = new HttpParams()
            .set('corpus', corpusId)
            .set('samples', samples);
        return this.http.get<CorpusDataFile[]>('/api/corpus/datafiles/', {
            params: params,
        });
    }

    public getDataFileInfo(dataFile: CorpusDataFile): Observable<DataFileInfo> {
        return this.http.get<DataFileInfo>(
            `/api/corpus/datafiles/${dataFile.id}/info/`
        );
    }

    // Tagging

    public userTags(): Observable<Tag[]> {
        const url = this.apiRoute(this.tagApiUrl, 'tags/');
        return this.http.get<Tag[]>(url);
    }

    public createTag(name: string, description?: string): Observable<Tag> {
        const url = this.apiRoute(this.tagApiUrl, 'tags/');
        return this.http.post<Tag>(url, { name, description });
    }

    public deleteTag(tag: Tag): Observable<null> {
        const url = this.apiRoute(this.tagApiUrl, `tags/${tag.id}/`);
        return this.http.delete<null>(url);
    }

    public patchTag(tagId: number, fields: Partial<Tag>): Observable<Tag> {
        const url = this.apiRoute(this.tagApiUrl, `tags/${tagId}/`);
        return this.http.patch<Tag>(url, fields);
    }

    public documentTags(
        document: FoundDocument
    ): Observable<DocumentTagsResponse> {
        const url = this.apiRoute(
            this.tagApiUrl,
            `document_tags/${document.corpus.name}/${document.id}`
        );
        return this.http.get<DocumentTagsResponse>(url);
    }

    public setDocumentTags(
        document: FoundDocument,
        tagIds: number[]
    ): Observable<DocumentTagsResponse> {
        const url = this.apiRoute(
            this.tagApiUrl,
            `document_tags/${document.corpus.name}/${document.id}`
        );
        return this.http.patch<DocumentTagsResponse>(url, { tags: tagIds });
    }

    // Authentication API
    public login(username: string, password: string) {
        return this.http.post<{ key: string }>(this.authApiRoute('login'), {
            username,
            password,
        });
    }

    public logout() {
        return this.http.post<{ detail: string }>(
            this.authApiRoute('logout'),
            {}
        );
    }

    public getUser() {
        return this.http.get<UserResponse>(this.authApiRoute('user'));
    }

    public register(details: {
        username: string;
        email: string;
        password1: string;
        password2: string;
    }) {
        return this.http.post<any>(this.authApiRoute('registration'), details);
    }

    public verify(key: string) {
        return this.http.post<any>(
            this.authApiRoute('registration/verify-email'),
            { key }
        );
    }

    public keyInfo(key: string) {
        return this.http.post<{ username: string; email: string }>(
            this.authApiRoute('registration/key-info'),
            { key }
        );
    }

    public requestResetPassword(email: string) {
        return this.http.post<{ detail: string }>(
            this.authApiRoute('password/reset'),
            { email }
        );
    }

    public resetPassword(
        uid: string,
        token: string,
        newPassword1: string,
        newPassword2: string
    ) {
        return this.http.post<{ detail: string }>(
            this.authApiRoute('password/reset/confirm'),
            {
                uid,
                token,
                new_password1: newPassword1,
                new_password2: newPassword2,
            }
        );
    }

    /** send PATCH request to update settings for the user */
    public updateUserSettings(
        details: Partial<UserResponse>
    ): Observable<UserResponse> {
        return this.http.patch<UserResponse>(
            this.authApiRoute('user'),
            details
        );
    }

    public solisLogin(data: any): Promise<SolisLoginResponse> {
        return this.http.get<SolisLoginResponse>('/api/solislogin').toPromise();
    }
}
