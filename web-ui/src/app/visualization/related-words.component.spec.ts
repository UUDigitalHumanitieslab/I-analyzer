import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { FormsModule } from '@angular/forms';
import { ChartModule } from 'primeng/primeng'

import { ManualService, SearchService } from '../services/index';
import { ManualServiceMock } from '../services/manual.service.mock';
import { SearchServiceMock } from '../services/search.service.mock';
import { RelatedWordsComponent } from './related-words.component';

describe('RelatedWordsComponent', () => {
  let component: RelatedWordsComponent;
  let fixture: ComponentFixture<RelatedWordsComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      imports: [ FormsModule, ChartModule ],
      declarations: [ RelatedWordsComponent ],
      providers: [
        { provide: SearchService, useValue: new SearchServiceMock()},
        { provide: ManualService, useClass: ManualServiceMock },
      ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(RelatedWordsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
