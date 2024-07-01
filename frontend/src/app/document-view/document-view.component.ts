import { Component, Input, OnChanges, SimpleChanges } from '@angular/core';

import { CorpusField, FoundDocument, Corpus, QueryModel } from '../models/index';
import { DocumentView } from '../models/document-page';
import * as _ from 'lodash';
import { documentIcons, entityIcons } from '../shared/icons';

@Component({
    selector: 'ia-document-view',
    templateUrl: './document-view.component.html',
    styleUrls: ['./document-view.component.scss']
})
export class DocumentViewComponent implements OnChanges {

    @Input()
    public document: FoundDocument;

    @Input()
    public queryModel: QueryModel;

    @Input()
    public corpus: Corpus;

    @Input()
    public view: DocumentView;

    @Input()
    public showEntities: boolean;

    documentIcons = documentIcons;
    entityIcons = entityIcons;

    /** active tab on opening */
    activeTab: string;

    public imgNotFound: boolean;
    public imgPath: string;
    public media: string[];
    public allowDownload: boolean;
    public mediaType: string;

    constructor() { }

    get contentFields() {
        return this.corpus.fields.filter(field => !field.hidden && field.displayType === 'text_content');
    }

    get propertyFields() {
        return this.corpus.fields.filter(field => !field.hidden && field.displayType !== 'text_content');
    }

    get showScanTab() {
        return !!this.corpus.scanImageType;
    }

    ngOnChanges(changes: SimpleChanges): void {
        if (changes.view) {
            this.activeTab = this.tabFromView(this.view);
        }
    }

    /** get the tab from the view mode
     *
     * For "scan" view: select the scan tab if there is one
     * For "content" view: select the first content field
     */
    tabFromView(view: DocumentView): string {
        if (view === 'scan' && this.showScanTab) {
            return 'scan';
        }
        return _.first(this.contentFields)['name'];
    }

    isUrlField(field: CorpusField) {
        return field.displayType === 'url';
    }

    isGeoPointField(field: CorpusField) {
        return field.mappingType === 'geo_point';
    }

}
