import { BehaviorSubject } from 'rxjs';
import { Store } from './types';
import { Params } from '@angular/router';
import * as _ from 'lodash';
import { map, scan } from 'rxjs/operators';
import { mergeParams, omitNullParameters } from '../utils/params';

/** simple store that does not depend on services or routing
 *
 * Stores parameters in an internal BehaviorSubject. Can be used
 * for testing or to manage stand-alone models.
 */
export class SimpleStore implements Store {
    paramUpdates$ = new BehaviorSubject<Params>({});
    params$ = new BehaviorSubject<Params>({});

    constructor() {
        this.paramUpdates$.pipe(
            scan(mergeParams),
            map(omitNullParameters),
            map(obj => _.mapValues(obj, _.toString)),
        ).subscribe(params =>
            this.params$.next(params)
        );
    }

    currentParams(): Params {
        return this.params$.value;
    }
};
