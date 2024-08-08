import { Component, output } from '@angular/core';

import { actionIcons } from '../../shared/icons';
import { DialogService } from '../../services';

@Component({
  selector: 'ia-entity-toggle',
  imports: [],
  templateUrl: './entity-toggle.component.html',
  styleUrl: './entity-toggle.component.scss'
})
export class EntityToggleComponent {
    actionIcons = actionIcons;
    toggleNER = output<Boolean>();

    constructor(private dialogService: DialogService) {}

    public showNamedEntityDocumentation() {
        this.dialogService.showManualPage('namedentities');
    }
}
