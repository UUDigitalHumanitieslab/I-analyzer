import { Component, EventEmitter, Input, OnDestroy, Output } from '@angular/core';
import { formIcons } from '../../../shared/icons';
import { RouterStoreService } from '../../../store/router-store.service';
import { ComparedQueries } from '../../../models/compared-queries';
import { Observable } from 'rxjs';
import * as _ from 'lodash';
import { map } from 'rxjs/operators';

@Component({
    selector: 'ia-term-comparison-editor',
    templateUrl: './term-comparison-editor.component.html',
    styleUrls: ['./term-comparison-editor.component.scss'],
})
export class TermComparisonEditorComponent implements OnDestroy {
    @Input() termLimit = 10;

    @Output() queriesChanged = new EventEmitter<string[]>();
    @Output() clearQueries = new EventEmitter<void>();

    comparedQueries: ComparedQueries;

    queries: string[] = [];
    showReset$: Observable<boolean>;

    formIcons = formIcons;

    constructor(
        private routerStoreService: RouterStoreService,
    ) {
        this.comparedQueries = new ComparedQueries(this.routerStoreService);

        // note that state$ and allQueries$ are completed by this component's ngOnDestroy
        this.comparedQueries.state$.subscribe(state => this.queries = state.compare);
        this.comparedQueries.allQueries$.subscribe(this.queriesChanged);

        this.showReset$ = this.comparedQueries.state$.pipe(
            map(state => !_.isEmpty(state.compare))
        );
    }

    valid(queryInput: string[]) {
        return queryInput.length <= this.termLimit;
    }

    ngOnDestroy(): void {
        this.comparedQueries.complete();
    }

    confirmQueries() {
        this.comparedQueries.setParams({compare: this.queries});
    }

    reset() {
        this.comparedQueries.reset();
        this.clearQueries.emit();
    }
}
