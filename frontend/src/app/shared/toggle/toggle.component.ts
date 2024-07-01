import { Component, EventEmitter, OnInit, Output } from '@angular/core';

@Component({
  selector: 'ia-toggle',
  templateUrl: './toggle.component.html',
  styleUrls: ['./toggle.component.scss']
})
export class ToggleComponent implements OnInit {
  @Output() toggled = new EventEmitter<boolean>();
  active = false;

  constructor() { }

  ngOnInit(): void {
  }

  public toggleButton() {
    this.active = !this.active;
    this.toggled.emit(this.active);
  }

}
