import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FieldFormComponent } from './field-form.component';
import { CorpusDefinitionService } from 'app/corpus-definitions/corpus-definition.service';

describe('FieldFormComponent', () => {
    let component: FieldFormComponent;
    let fixture: ComponentFixture<FieldFormComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            declarations: [FieldFormComponent],
            providers: [CorpusDefinitionService],
        }).compileComponents();

        fixture = TestBed.createComponent(FieldFormComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
