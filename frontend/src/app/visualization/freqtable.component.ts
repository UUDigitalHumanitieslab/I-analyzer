import { Input, Component, OnChanges, OnDestroy, ViewEncapsulation, SimpleChanges } from '@angular/core';
import * as _ from 'lodash';
import { saveAs } from 'file-saver';
import { freqTableHeader, freqTableHeaders } from '../models';

@Component({
    selector: 'ia-freqtable',
    templateUrl: './freqtable.component.html',
    styleUrls: ['./freqtable.component.scss'],
    encapsulation: ViewEncapsulation.None
})
export class FreqtableComponent {
    @Input() headers: freqTableHeaders;
    @Input() data: any[];
    @Input() name: string;
    @Input() defaultSort: string;
    public defaultSortOrder = '-1';

    constructor() { }

    parseTableData(): string[] {
        const data = this.data.map(row => {
            const values = this.headers.map(col => this.getValue(row, col));
            return  `${_.join(values, ',')}\n`;
        });
        data.unshift(`${_.join(this.headers.map(col => col.label), ',')}\n`);
        return data;
    }

    getValue(row, column: freqTableHeader) {
        if (column.formatDownload) {
            return column.formatDownload(row[column.key]);
        }
        if (column.format) {
            return column.format(row[column.key]);
        }
        return row[column.key];
    }

    downloadTable() {
        const data = this.parseTableData();
        const blob = new Blob(data, { type: `text/csv;charset=utf-8`, endings: 'native' });
        const filename = this.name + '.csv';
        saveAs(blob, filename);
    }
}
