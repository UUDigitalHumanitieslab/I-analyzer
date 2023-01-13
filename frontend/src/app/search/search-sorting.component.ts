import { Component, Input } from '@angular/core';
import { ActivatedRoute, ParamMap, Router } from '@angular/router';
import { CorpusField } from '../models';
import { ParamDirective } from '../param/param-directive';
import { ParamService } from '../services';

const defaultValueType = 'alpha';
@Component({
    selector: 'ia-search-sorting',
    templateUrl: './search-sorting.component.html',
    styleUrls: ['./search-sorting.component.scss'],
    host: { 'class': 'field has-addons' }
})
export class SearchSortingComponent extends ParamDirective {
    @Input()
    public set fields(fields: CorpusField[]) {
        this.sortableFields = fields.filter(field => field.sortable);
    }

    private sortData: {
        field: CorpusField
        ascending: boolean
    }
    public ascending = true;
    public primarySort: CorpusField;
    public sortField: CorpusField;

    public valueType: 'alpha' | 'numeric' = defaultValueType;
    public sortableFields: CorpusField[];
    public showFields = false;

    public get sortType(): SortType {
        return `${this.valueType}${this.ascending ? 'Asc' : 'Desc'}` as SortType;
    }

    constructor(
        route: ActivatedRoute,
        router: Router,
        private paramService: ParamService
    ) {
        super(route, router);
    }

    initialize() {
        this.primarySort = this.sortableFields.find(field => field.primarySort);
        this.sortField = this.primarySort;
    }

    teardown() {
        this.setParams({ sort: null });
    }

    setStateFromParams(params: ParamMap) {
        this.sortData = this.paramService.setSortFromParams(params, this.sortableFields);
        this.sortField = this.sortData.field;
        this.ascending = this.sortData.ascending;
    }

    public toggleSortType() {
        this.ascending = !this.ascending;
        this.emitChange();
    }

    public toggleShowFields() {
        this.showFields = !this.showFields;
    }

    public changeField(field: CorpusField | undefined) {
        if (field === undefined) {
            this.valueType = defaultValueType;
            this.ascending = false;
        } else {
            this.valueType = ['integer', 'date', 'boolean'].indexOf(field.displayType) >= 0 ? 'numeric' : 'alpha';
        }
        this.sortField = field;
        this.emitChange();
    }

    private emitChange() {
        const sortField = this.sortData ? this.sortData.field : this.primarySort;
        const setting = this.paramService.makeSortParams(sortField, this.ascending? 'asc': 'desc');
        this.setParams(setting);
    }
}

type SortType = 'alphaAsc' | 'alphaDesc' | 'numericAsc' | 'numericDesc';
