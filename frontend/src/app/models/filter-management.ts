import { CorpusField } from './corpus';
import { QueryModel } from './query';
import { SearchFilter } from './search-filter';

export class PotentialFilter {
    filter: SearchFilter;
    useAsFilter: boolean;
    showReset?: boolean;
    grayedOut?: boolean;
    adHoc?: boolean;

    constructor(public corpusField: CorpusField, public queryModel: QueryModel) {
        this.filter = corpusField.makeSearchFilter();
        this.useAsFilter = false;
        if (!corpusField.filterOptions) {
            this.adHoc = true;
        }
    }

    toggle() {
        this.useAsFilter = !this.useAsFilter;
        if (this.useAsFilter) {
            this.queryModel.addFilter(this.filter);
        } else {
            this.queryModel.removeFilter(this.filter);
        }
    }

    deactivate() {
        if (this.useAsFilter) {
            this.toggle();
        }
    }

    reset() {
        this.deactivate();
        this.filter.reset();
    }
}
