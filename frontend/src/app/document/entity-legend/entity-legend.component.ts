import { Component, Input, OnChanges } from '@angular/core';
import * as _ from 'lodash';

import { entityIcons } from '../../shared/icons';
import { FieldEntities } from '../../models';

@Component({
  selector: 'ia-entity-legend',
  templateUrl: './entity-legend.component.html',
  styleUrls: ['./entity-legend.component.scss']
})
export class EntityLegendComponent implements OnChanges {
    @Input() entityAnnotations: FieldEntities[];

    public entityIcons = entityIcons;
    public entities: string[];

    constructor() { }

    ngOnChanges(): void {
        if (!this.entityAnnotations) {
            this.entities = null;
        } else {
            this.entities = _.uniq(this.entityAnnotations.map((item) => item.entity)).filter((value) => value !=='flat');
        }
    }

}
