import { ComponentFixture, TestBed } from '@angular/core/testing';

import { UploadSampleComponent } from './upload-sample.component';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { CorpusDefinitionService } from 'app/corpus-definitions/corpus-definition.service';
import { SlugifyPipe } from '@shared/pipes/slugify.pipe';

describe('UploadSampleComponent', () => {
    let component: UploadSampleComponent;
    let fixture: ComponentFixture<UploadSampleComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            declarations: [UploadSampleComponent],
            imports: [HttpClientTestingModule],
            providers: [CorpusDefinitionService, SlugifyPipe],
        }).compileComponents();

        fixture = TestBed.createComponent(UploadSampleComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
