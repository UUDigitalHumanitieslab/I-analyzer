import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { Corpus, NamedEntitiesResult } from '../models';

@Injectable({
    providedIn: 'root',
})
export class EntityService {

    constructor(private http: HttpClient) {
    }

    public getDocumentEntities(corpus: Corpus, id: string): Observable<NamedEntitiesResult> {
        const url = `/api/es/${corpus.name}/${id}/named_entities`;
        return this.http.get<NamedEntitiesResult>(url);
    }
}
