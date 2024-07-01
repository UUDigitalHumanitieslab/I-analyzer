import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import * as _ from 'lodash';
import { mockCorpus, mockField } from '../../mock-data/corpus';

import { commonTestBed } from '../common-test-bed';

import { DocumentViewComponent } from './document-view.component';
import { makeDocument } from '../../mock-data/constructor-helpers';

describe('DocumentViewComponent', () => {
    let component: DocumentViewComponent;
    let fixture: ComponentFixture<DocumentViewComponent>;

    beforeEach(waitForAsync(() => {
        commonTestBed().testingModule.compileComponents();
    }));

    beforeEach(() => {
        fixture = TestBed.createComponent(DocumentViewComponent);
        component = fixture.componentInstance;
        component.corpus = _.merge({
            scanImageType: 'farout_image_type'
        }, mockCorpus);
        component.document = makeDocument({ great_field: 'Hello world!', speech: 'Wally was last seen in Paris' });
        fixture.detectChanges();
    });

    it('should be created', () => {
        expect(component).toBeTruthy();
    });

    it('should render fields', () => {
        expect(component.propertyFields).toEqual([mockField]);
        const debug = fixture.debugElement.queryAll(By.css('[data-test-field-value]'));
        expect(debug.length).toEqual(1); // number of fields
        const element = debug[0].nativeElement;
        expect(element.textContent).toBe('Hello world!');
    });

    it('should create tabs', () => {
        const debug = fixture.debugElement.queryAll(By.css('a[role=tab]'));
        expect(debug.length).toBe(2);
        expect(debug[0].attributes['id']).toBe('tab-speech');
        expect(debug[1].attributes['id']).toBe('tab-scan');
    });

    it('shows a named entity legend if showEntities is true', () => {
        expect(fixture.debugElement.query(By.css('ia-entity-legend'))).toBeFalsy();
        component.showEntities = true;
        fixture.detectChanges();
        expect(fixture.debugElement.query(By.css('ia-entity-legend'))).toBeTruthy();
    });

});
