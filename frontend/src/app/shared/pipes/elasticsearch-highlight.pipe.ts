import { Pipe, PipeTransform } from '@angular/core';
import * as _ from 'lodash';

import { CorpusField, FoundDocument } from '../../models';

@Pipe({
    name: 'elasticsearchHighlight'
})
export class ElasticsearchHighlightPipe implements PipeTransform {

    /**
     * Transforms a text to display highlights fetched from Elasticsearch
     *
     * @param document a FoundDocument, containing the fetched highlights
     */
    transform(field: CorpusField, document: FoundDocument) {
        const fieldValue = document.fieldValues[field.name];

        if (_.isEmpty(fieldValue)) {
            return;
        }

        const highlighted = this.highlightedInnerHtml(field, document);
        return highlighted;
    }

    highlightedInnerHtml(field: CorpusField, document: FoundDocument) {
        let highlighted = document.fieldValues[field.name];
        if (document.highlight && document.highlight.hasOwnProperty(field.name)) {
                for (const highlight of document.highlight[field.name]) {
                    const strippedHighlight = this.stripTags(highlight);
                    highlighted = highlighted.replace(strippedHighlight, highlight);
                }
            }
        return highlighted;
    }

    stripTags(htmlString: string){
        const parseHTML= new DOMParser().parseFromString(htmlString, 'text/html');
        return parseHTML.body.textContent || '';
    }

}
