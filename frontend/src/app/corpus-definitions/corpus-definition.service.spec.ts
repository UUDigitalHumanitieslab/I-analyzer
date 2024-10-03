import { TestBed } from '@angular/core/testing';

import { CorpusDefinitionService } from './corpus-definition.service';
import { SlugifyPipe } from '@shared/pipes/slugify.pipe';

describe('CorpusDefinitionService', () => {
    let service: CorpusDefinitionService;

    beforeEach(() => {
        TestBed.configureTestingModule({
            providers: [CorpusDefinitionService, SlugifyPipe],
        });
        service = TestBed.inject(CorpusDefinitionService);
    });

    it('should be created', () => {
        expect(service).toBeTruthy();
    });
});
