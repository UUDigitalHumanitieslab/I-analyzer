import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { actionIcons } from '@shared/icons';

@Component({
  selector: 'ia-full-data-button',
  templateUrl: './full-data-button.component.html',
  styleUrls: ['./full-data-button.component.scss']
})
export class FullDataButtonComponent {
    @Output() requestFullData = new EventEmitter<void>();

    isLoading = false; // show loading spinner in button
    showModal = false;

    actionIcons = actionIcons;

    constructor() { }

    onInitialRequest() {
        this.showModal = true;
    }

    async showLoading(promise: Promise<any>) {
        this.isLoading = true;
        await promise;
        this.isLoading = false;
    }


    onConfirm() {
        this.showModal = false;
        this.requestFullData.emit();
    }

}
