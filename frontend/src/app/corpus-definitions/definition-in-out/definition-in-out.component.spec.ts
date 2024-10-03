import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';

import { DefinitionInOutComponent } from './definition-in-out.component';
import { commonTestBed } from '../../common-test-bed';

describe('EditDefinitionComponent', () => {
    let component: DefinitionInOutComponent;
    let fixture: ComponentFixture<DefinitionInOutComponent>;

    beforeEach(waitForAsync(() => {
        commonTestBed().testingModule.compileComponents();
    }));

    beforeEach(() => {
        fixture = TestBed.createComponent(DefinitionInOutComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
