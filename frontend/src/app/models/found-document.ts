import * as _ from 'lodash';
import { makeContextParams } from '../utils/document-context';
import { Corpus, CorpusField } from './corpus';
import { FieldValues, HighlightResult, SearchHit } from './elasticsearch';
import { Tag } from './tag';
import { Observable, Subject, merge, timer } from 'rxjs';
import { TagService } from '../services/tag.service';
import { map, mergeMap, shareReplay, take, tap } from 'rxjs/operators';

export class FoundDocument {
    id: string;

    /** relevance score for the query;
     * in [0,1] with 1 being most relevant
     */
    relevance: number;

    /** values for fields */
    fieldValues: FieldValues;

    /** position of the document in the array of results */
    position: number;

    /** highlighted strings */
    highlight: HighlightResult;

    /** tags created on the document */
    tags$: Observable<Tag[]>;

    private tagsChanged$ = new Subject<void>();

    constructor(
        public corpus: Corpus,
        hit: SearchHit,
        maxScore: number = 1,
        private tagService?: TagService
    ) {
        this.id = hit._id;
        this.relevance = hit._score / maxScore;
        this.fieldValues = Object.assign({ id: hit._id }, hit._source);
        this.highlight = hit.highlight;

        // tags need to refreshed when the document is created, and
        // after each update
        if (this.tagService) {
            const created$ = timer(); // observable of the moment of construction (i.e. now)
            this.tags$ = merge(created$, this.tagsChanged$).pipe(
                mergeMap(() => this.fetchTags()),
                shareReplay(1),
            );
        }
    }

    /**
     * whether the document has a "context" that it belongs to
     *
     * e.g. the publication it was a part of
     */
    get hasContext(): boolean {
        const spec = this.corpus.documentContext;

        if (_.isUndefined(spec)) {
            return false;
        }

        const notBlank = (value) =>
            value !== undefined && value !== null && value !== '';
        const contextValues = spec.contextFields.map(
            this.fieldValue.bind(this)
        );
        return _.every(contextValues, notBlank);
    }

    /**
     * query parameters for a search request for the context of the document
     *
     * e.g. the publication it was a part of
     */
    get contextQueryParams() {
        return makeContextParams(this, this.corpus);
    }

    fieldValue(field: CorpusField) {
        return this.fieldValues[field.name];
    }

    language(field: CorpusField) {
        if (field.language === 'dynamic') {
            return this.fieldValue(this.corpus.languageField);
        }
        else {
            return field.language;
        }
    }

    addTag(tag: Tag): void {
        this.tags$.pipe(
            take(1),
            map(tags => tags.concat([tag])),
            mergeMap(tags => this.setTags(tags)),
        ).subscribe(() =>
            this.tagsChanged$.next()
        );
    }

    removeTag(tag: Tag): void {
        this.tags$.pipe(
            take(1),
            map(tags => _.without(tags, tag)),
            mergeMap(tags => this.setTags(tags)),
        ).subscribe(() =>
            this.tagsChanged$.next()
        );
    }

    private setTags(tags: Tag[]): Observable<Tag[]> {
        return this.tagService.setDocumentTags(this, tags);
    }

    private fetchTags(): Observable<Tag[]> {
        return this.tagService.getDocumentTags(this);
    }
}
