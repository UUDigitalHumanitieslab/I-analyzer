import { ComponentFixture, TestBed } from '@angular/core/testing';

import { commonTestBed } from '../../common-test-bed';
import { EntityToggleComponent } from './entity-toggle.component';

describe('EntityToggleComponent', () => {
  let component: EntityToggleComponent;
  let fixture: ComponentFixture<EntityToggleComponent>;

  beforeEach(async () => {
    await commonTestBed().testingModule.compileComponents();

    fixture = TestBed.createComponent(EntityToggleComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
