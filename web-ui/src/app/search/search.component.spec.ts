import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { ActivatedRoute } from '@angular/router';
import { FormsModule } from '@angular/forms';

import { Observable } from 'rxjs';

import { CalendarModule, SelectButtonModule, SliderModule } from 'primeng/primeng';

import * as corpus from '../../mock-data/corpus';
import { ApiService, CorpusService, SearchService } from '../services/index';
import { ApiServiceMock } from '../services/api.service.mock';

import { SearchComponent } from './search.component';
import { SearchFilterComponent } from './search-filter.component';
import { SearchSampleComponent } from './search-sample.component';

describe('SearchComponent', () => {
    let component: SearchComponent;
    let fixture: ComponentFixture<SearchComponent>;

    beforeEach(async(() => {
        TestBed.configureTestingModule({
            declarations: [SearchComponent, SearchFilterComponent, SearchSampleComponent],
            imports: [FormsModule, CalendarModule, SelectButtonModule, SliderModule],
            providers: [
                CorpusService,
                { provide: ApiService, useValue: new ApiServiceMock({
                    ['corpus']: corpus.foo
                }) },
                SearchService,
                {
                    provide: ActivatedRoute, useValue: {
                        params: Observable.of({ corpus: 'test' })
                    }
                }]
        }).compileComponents();
    }));

    beforeEach(() => {
        fixture = TestBed.createComponent(SearchComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should be created', () => {
        expect(component).toBeTruthy();
    });
});
