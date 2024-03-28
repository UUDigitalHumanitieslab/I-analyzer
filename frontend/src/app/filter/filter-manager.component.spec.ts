import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';
import { By } from '@angular/platform-browser';

import { commonTestBed } from '../common-test-bed';

import { FilterManagerComponent } from './filter-manager.component';
import { mockCorpus, mockCorpus2 } from '../../mock-data/corpus';
import { QueryModel } from '../models';

import { AuthService } from '../services';
import { UnauthenticatedMock } from '../../mock-data/auth';

describe('FilterManagerComponent', () => {
    let component: FilterManagerComponent;
    let fixture: ComponentFixture<FilterManagerComponent>;

    beforeEach(waitForAsync(() => {
        commonTestBed().testingModule.compileComponents();
    }));

    describe('it works for an authenticated user:', () => {
        beforeEach(() => {
            fixture = TestBed.createComponent(FilterManagerComponent);
            component = fixture.componentInstance;
            component.queryModel = new QueryModel(mockCorpus, true);
            fixture.detectChanges();
        });

        it('should create', () => {
            expect(component).toBeTruthy();
            expect(component.filters.length).toEqual(3);
        });

        it('resets filters when corpus changes', () => {
            component.queryModel = new QueryModel(mockCorpus2, true);
            fixture.detectChanges();
            expect(component.filters.length).toEqual(2);
            expect(component.filters[0]['adHoc']).toBeTrue();
            component.queryModel = new QueryModel(mockCorpus, true);
            fixture.detectChanges();
            expect(component.filters.length).toEqual(3);
            expect(component.filters[0]['adHoc']).toBeFalse();
        });

        it('toggles filters on and off', async () => {
            const filter = component.filters.find(f => f['corpusField']['name'] === 'great_field');
            expect(component.activeFilters.length).toBe(0);
            filter.set(true);
            expect(component.activeFilters.length).toBe(1);
            filter.toggle();
            expect(component.activeFilters.length).toBe(0);
            filter.toggle();
            expect(component.activeFilters.length).toBe(1);
        });

        it('shows tag filter', async () => {
            component.queryModel = new QueryModel(mockCorpus, true);
            await fixture.whenStable();
            const compiled = fixture.debugElement;
            const tagFilter = compiled.query(By.css('ia-tag-filter'));
            expect(tagFilter).toBeTruthy();
        });
    });

    describe('it behaves differently for unauthenticated user:', () => {
        beforeEach(() => {
            TestBed.overrideProvider(AuthService, {useValue: new UnauthenticatedMock()});
            fixture = TestBed.createComponent(FilterManagerComponent);
            component = fixture.componentInstance;
            component.queryModel = new QueryModel(mockCorpus);
            fixture.detectChanges();
        });

        it('does not show tag filter', async () => {
            await fixture.whenStable();
            const compiled = fixture.debugElement;
            const tagFilter = compiled.query(By.css('ia-tag-filter'));
            expect(tagFilter).toBeFalsy();
        });
    });


});
