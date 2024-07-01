/* eslint-disable @typescript-eslint/member-ordering */
import { Injectable } from '@angular/core';

import { BehaviorSubject } from 'rxjs';

import { Corpus, CorpusField, DocumentContext, SortDirection, SortState } from '../models/index';
import { ApiRetryService } from './api-retry.service';
import { AuthService } from './auth.service';
import { findByName } from '../utils/utils';
import * as _ from 'lodash';

@Injectable({
    providedIn: 'root',
})
export class CorpusService {
    private currentCorpusSubject = new BehaviorSubject<Corpus | undefined>(
        undefined
    );

    public currentCorpus = this.currentCorpusSubject.asObservable();

    public corporaPromise: Promise<Corpus[]>;

    constructor(
        private apiRetryService: ApiRetryService,
        private authService: AuthService
    ) {
        this.parseField = this.parseField.bind(this);
    }

    /**
     * Sets a corpus and returns a boolean indicating whether the corpus exists and is accessible.
     *
     * @param corpusName Name of the corpus
     */
    public set(corpusName: string): Promise<boolean> {
        if (
            this.currentCorpusSubject.value &&
            this.currentCorpusSubject.value.name === corpusName
        ) {
            // no need to retrieve the corpus again if nothing changed
            return Promise.resolve(true);
        }
        return this.get().then((all) => {
            const corpus = findByName(all, corpusName);
            if (!corpus) {
                return false;
            } else {
                this.currentCorpusSubject.next(corpus);
                return true;
            }
        });
    }

    /**
     * retrieve the available corpora
     *
     * @param refresh if `true`, forces the corpus list to be requested from the backend
     * regardless of whether a list of corpora has already been loaded.
     * @returns Promise object with list of all corpora
     */
    public get(refresh = false): Promise<Corpus[]> {
        if (!refresh && this.corporaPromise) {
            return this.corporaPromise;
        } else {
            this.corporaPromise = this.apiRetryService
                .requireLogin((api) => api.corpus().toPromise())
                .then((data) => this.parseCorpusList(data));
            return this.corporaPromise;
        }
    }

    private async parseCorpusList(data: any): Promise<Corpus[]> {
        return data.map(this.parseCorpusItem);
    }

    private parseCorpusItem = (data: any): Corpus => {
        const allFields: CorpusField[] = data.fields.map(this.parseField);
        return new Corpus(
            data.name,
            data.title,
            data.description,
            data.es_index,
            allFields,
            new Date(data.min_date),
            new Date(data.max_date),
            data.scan_image_type,
            data.allow_image_download,
            data.word_models_present,
            data.languages,
            data.category,
            data.has_named_entities,
            this.parseDocumentContext(data.document_context, allFields),
            data.new_highlight,
            this.parseDefaultSort(data.default_sort, allFields),
            findByName(allFields, data.language_field),
        );
    };

    private parseField = (data: any): CorpusField => new CorpusField(data);

    private parseDocumentContext(
        data: {
            context_fields: string[] | null;
            sort_field: string | null;
            context_display_name: string | null;
            sort_direction: 'string' | null;
        },
        allFields: CorpusField[]
    ): DocumentContext {
        if (_.isEmpty(data) || !data.context_fields) {
            return undefined;
        }

        const contextFields = allFields.filter((field) =>
            data.context_fields.includes(field.name)
        );

        if (!contextFields) {
            return undefined;
        }

        const sortField = allFields.find(
            (field) => field.name === data.sort_field
        );
        const displayName = data.context_display_name || contextFields[0].name;
        const sortDirection = (data.sort_direction as 'asc' | 'desc') || 'asc';

        return {
            contextFields,
            sortField,
            displayName,
            sortDirection,
        };
    }

    private parseDefaultSort(
        data: { field: string; ascending: boolean},
        allFields: CorpusField[]
    ): SortState {
        if (data) {
            const field = findByName(allFields, data.field);
            const direction: SortDirection = data.ascending ? 'asc' : 'desc';
            return [field, direction];
        } else {
            return [undefined, 'desc'];
        }
    }
}
