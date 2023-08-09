import { Injectable } from '@angular/core';
import { FoundDocument } from '../models';
import { Observable } from 'rxjs';
import { Tag } from '../models';
import { map, tap } from 'rxjs/operators';
import { ApiService } from './api.service';


@Injectable({
    providedIn: 'root'
})
export class TagService {
    /** all tags from the user */
    tags$: Observable<Tag[]>;

    constructor(private apiService: ApiService) {
        this.fetch();
    }

    makeTag(name: string, description?: string): Observable<Tag> {
        return this.apiService.createTag(name, description).pipe(
            tap(this.fetch.bind(this))
        );
    }

    getDocumentTags(document: FoundDocument): Observable<Tag[]> {
        return this.apiService.documentTags(document).pipe(
            map(response => response.tags)
        );
    }

    setDocumentTags(document: FoundDocument, tagIds: number[]): Observable<Tag[]> {
        return this.apiService.setDocumentTags(document, tagIds).pipe(
            map(response => response.tags)
        );
    }

    private fetch() {
        this.tags$ = this.apiService.userTags();
    }
}
