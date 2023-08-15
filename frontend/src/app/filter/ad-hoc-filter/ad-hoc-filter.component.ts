import { Component } from '@angular/core';
import { AdHocFilter, } from '../../models';
import { BaseFilterComponent } from '../base-filter.component';

@Component({
  selector: 'ia-ad-hoc-filter',
  templateUrl: './ad-hoc-filter.component.html',
  styleUrls: ['./ad-hoc-filter.component.scss']
})
export class AdHocFilterComponent extends BaseFilterComponent<AdHocFilter> {
}
