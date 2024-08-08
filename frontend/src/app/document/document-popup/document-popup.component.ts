import { Component, Input, OnChanges, OnDestroy, SimpleChanges } from '@angular/core';
import { DocumentFocus, DocumentPage, DocumentView } from '../../models/document-page';
import { takeUntil } from 'rxjs/operators';
import * as _ from 'lodash';
import { FoundDocument, QueryModel } from '../../models';
import { Subject } from 'rxjs';
import { actionIcons, documentIcons } from '../../shared/icons';

@Component({
    selector: 'ia-document-popup',
    templateUrl: './document-popup.component.html',
    styleUrls: ['./document-popup.component.scss']
})
export class DocumentPopupComponent implements OnChanges, OnDestroy {
    @Input() page: DocumentPage;
    @Input() queryModel: QueryModel;

    document: FoundDocument;
    view: DocumentView;

    visible = true;

    actionIcons = actionIcons;
    documentIcons = documentIcons;

    showNamedEntities = false;
    showNEROption = false;

    private refresh$ = new Subject<void>();

    get documentPageLink(): string[] {
        if (this.document) {
            return ['/document', this.document.corpus.name, this.document.id];
        }
    }

    get contextDisplayName(): string {
        if (this.document.corpus.documentContext) {
            return this.document.corpus.documentContext.displayName;
        }
    }

    ngOnChanges(changes: SimpleChanges): void {
        if (changes.queryModel) {
            this.showNEROption = this.queryModel.corpus.hasNamedEntities;
        }
        if (changes.page) {
            this.refresh$.next();
            this.focusUpdate();

            this.page.focus$.pipe(
                takeUntil(this.refresh$),
            ).subscribe(this.focusUpdate.bind(this));
        }
    }

    ngOnDestroy(): void {
        this.refresh$.next();
        this.refresh$.complete();
    }

    focusUpdate(focus?: DocumentFocus): void {
        if (focus) {
            this.document = focus.document;
            this.view = focus.view;
            this.visible = true;
        } else {
            this.document = undefined;
            this.visible = false;
        }
    }

    toggleNER(active: boolean): void {
        this.showNamedEntities = active;
    }
}
