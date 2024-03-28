import { Injectable } from '@angular/core';
import { pick } from 'lodash';
import { BehaviorSubject, Observable } from 'rxjs';
import { map, tap } from 'rxjs/operators';
import { FoundDocument, Tag } from '../models';
import { ApiService } from './api.service';

@Injectable({
    providedIn: 'root',
})
export class TagService {
    /** all tags from the user */
    tags$ = new BehaviorSubject<Tag[]>(undefined);

    constructor(private apiService: ApiService) {}

    makeTag(name: string, description?: string): Observable<Tag> {
        return this.apiService
            .createTag(name, description)
            .pipe(tap(() => this.fetch()));
    }

    deleteTag(tag: Tag) {
        return this.apiService.deleteTag(tag).pipe(tap(() => this.fetch()));
    }

    updateTag(updatedTag: Tag) {
        const updateFields = pick(updatedTag, ['name', 'description']);
        return this.apiService
            .patchTag(updatedTag.id, updateFields)
            .pipe(tap(() => this.fetch()));
    }

    getDocumentTags(document: FoundDocument): Observable<Tag[]> {
        return this.apiService
            .documentTags(document)
            .pipe(map((response) => response.tags));
    }

    setDocumentTags(document: FoundDocument, tags: Tag[]): Observable<Tag[]> {
        const tagIds = tags.map((t) => t.id);
        return this.apiService
            .setDocumentTags(document, tagIds)
            .pipe(map((response) => response.tags));
    }

    fetch(): void {
        this.apiService.userTags().subscribe((tags) => this.tags$.next(tags));
    }
}
