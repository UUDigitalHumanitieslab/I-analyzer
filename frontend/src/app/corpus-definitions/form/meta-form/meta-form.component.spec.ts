import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MetaFormComponent } from './meta-form.component';
import { CorpusDefinitionService } from 'app/corpus-definitions/corpus-definition.service';
import { SlugifyPipe } from '@shared/pipes/slugify.pipe';

describe('MetaFormComponent', () => {
    let component: MetaFormComponent;
    let fixture: ComponentFixture<MetaFormComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            declarations: [MetaFormComponent],
            providers: [CorpusDefinitionService, SlugifyPipe],
        }).compileComponents();

        fixture = TestBed.createComponent(MetaFormComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
