import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { DropdownModule } from 'primeng/primeng';
import { TableModule } from 'primeng/table'

import { ApiService, ApiRetryService, LogService, SearchService, QueryService, UserService } from '../services/index';
import { ApiServiceMock } from '../services/api.service.mock';
import { SearchServiceMock } from '../services/search.service.mock';
import { UserServiceMock } from '../services/user.service.mock';
import { SearchHistoryComponent, QueryTextPipe, QueryFiltersComponent } from './index';


describe('SearchHistoryComponent', () => {
    let component: SearchHistoryComponent;
    let fixture: ComponentFixture<SearchHistoryComponent>;

    beforeEach(async(() => {
        TestBed.configureTestingModule({
            imports: [FormsModule, DropdownModule, TableModule],
            declarations: [QueryFiltersComponent, QueryTextPipe, SearchHistoryComponent],
            providers: [
                {
                    provide: ApiService, useValue: new ApiServiceMock({
                        'search_history': { queries: [] }
                    })
                },
                ApiRetryService,
                LogService,
                QueryService,
                {
                    provide: SearchService, useValue: new SearchServiceMock()
                },
                {
                    provide: Router, useValue: new RouterMock()
                },
                {
                    provide: UserService, useValue: new UserServiceMock()
                }
            ]
        }).compileComponents();

        fixture = TestBed.createComponent(SearchHistoryComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    }));

    it('should be created', () => {
        expect(component).toBeTruthy();
    });
});

class RouterMock {

}
