import { TestBed } from '@angular/core/testing';
import { ElementRef } from '@angular/core';
import { RouterTestingModule } from '@angular/router/testing';
import { HttpClientModule } from '@angular/common/http';

import { appRoutes, declarations, imports, providers } from './app.module';

import { ApiServiceMock } from '../mock-data/api';
import { AuthServiceMock } from '../mock-data/auth';
import { CorpusServiceMock } from '../mock-data/corpus';
import { DialogServiceMock } from '../mock-data/dialog';
import { ElasticSearchServiceMock } from '../mock-data/elastic-search';
import { EntityServiceMock } from '../mock-data/entity';
import { MockCorpusResponse } from '../mock-data/corpus-response';
import { SearchServiceMock } from '../mock-data/search';
import { ApiService, AuthService, CorpusService, DialogService, SearchService } from './services';
import { ElasticSearchService } from './services/elastic-search.service';
import { EntityService } from './services/entity.service';
import { WordmodelsService } from './services/wordmodels.service';
import { WordmodelsServiceMock } from '../mock-data/wordmodels';
import { VisualizationService } from './services/visualization.service';
import { visualizationServiceMock } from '../mock-data/visualization';
import { TagService } from './services/tag.service';
import { TagServiceMock } from '../mock-data/tag';
import { RouterStoreService } from './store/router-store.service';
import { SimpleStore } from './store/simple-store';

export const commonTestBed = () => {
    const filteredImports = imports.filter(value => !(value in [HttpClientModule]));
    filteredImports.push(RouterTestingModule.withRoutes(appRoutes));
    const filteredProviders = providers.filter(provider => !(
        provider in [ApiService, CorpusService, DialogService, ElasticSearchService, SearchService]));
    filteredProviders.push(
        {
            provide: ApiService,
            useValue: new ApiServiceMock({
                ['corpus']: MockCorpusResponse,
            }),
        },
        {
            provide: AuthService,
            useValue: new AuthServiceMock()
        },
        {
            provide: CorpusService, useValue: new CorpusServiceMock()
        },
        {
            provide: DialogService,
            useClass: DialogServiceMock,
        },
        {
            provide: ElasticSearchService,
            useValue: new ElasticSearchServiceMock(),
        },
        {
            provide: EntityService,
            useValue: new EntityServiceMock(),
        },
        {
            provide: ElementRef,
            useClass: MockElementRef,
        },
        {
            provide: SearchService,
            useValue: new SearchServiceMock(),
        },
        {
            provide: WordmodelsService,
            useValue: new WordmodelsServiceMock(),
        },
        {
            provide: VisualizationService,
            useValue: new visualizationServiceMock(),
        },
        {
            provide: TagService,
            useValue: new TagServiceMock(),
        },
        {
            provide: RouterStoreService,
            useValue: new SimpleStore()
        }
    );

    return {
        testingModule: TestBed.configureTestingModule({
            declarations,
            imports: filteredImports,
            providers: filteredProviders
        })
    };
};

export class MockElementRef {
 nativeElement = {};
}
