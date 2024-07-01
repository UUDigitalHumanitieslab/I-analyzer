import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EntityLegendComponent } from './entity-legend.component';

describe('EntitiesComponent', () => {
  let component: EntityLegendComponent;
  let fixture: ComponentFixture<EntityLegendComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ EntityLegendComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(EntityLegendComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
