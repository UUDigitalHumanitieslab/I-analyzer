import * as _ from 'lodash';
import { map, mergeMap, shareReplay, take } from 'rxjs/operators';

import { makeContextParams } from '../utils/document-context';
import { Corpus, CorpusField } from './corpus';
import { FieldValues, HighlightResult, SearchHit } from './elasticsearch';
import { Tag } from './tag';
import { Observable, Subject, merge, timer } from 'rxjs';
import { EntityService } from '../services/entity.service';
import { TagService } from '../services/tag.service';
import { FieldEntities } from './search-results';

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

    /** named entities associated with the document */
    entityAnnotations$: Observable<{[fieldName: string]: FieldEntities[]}>;
    private tagsChanged$ = new Subject<void>();

    constructor(
        private tagService: TagService,
        private entityService: EntityService,
        public corpus: Corpus,
        hit: SearchHit,
        maxScore: number = 1,
    ) {
        this.id = hit._id;
        this.relevance = hit._score / maxScore;
        this.fieldValues = Object.assign({ id: hit._id }, hit._source);
        this.highlight = hit.highlight;

        const created$ = timer(0); // observable of the moment of construction (i.e. now)

        // tags need to be refreshed when the document is created, and
        // after each update
        // shareReplay shares the value over all observers:
        // add/removeTag, async pipe in document-tags.component template
        this.tags$ = merge(created$, this.tagsChanged$).pipe(
            mergeMap(() => this.fetchTags()),
            shareReplay(1),
        );

        this.entityAnnotations$ = created$.pipe(
            mergeMap(() => this.fetchAnnotatedEntities()),
            shareReplay(1),
        );
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

    private fetchAnnotatedEntities(): Observable<{[fieldName: string]: FieldEntities[]}> {
        const response$ = this.entityService.getDocumentEntities(this.corpus, this.id);
        return response$.pipe(
            map( response => response.annotations || {} )
        );
    }

    private setTags(tags: Tag[]): Observable<Tag[]> {
        return this.tagService.setDocumentTags(this, tags);
    }

    private fetchTags(): Observable<Tag[]> {
        return this.tagService.getDocumentTags(this);
    }

}
