import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Http, HttpModule, Response } from '@angular/http';
import { RouterModule, Routes } from '@angular/router';

import { MarkdownModule } from 'ngx-md';
import { ButtonModule, CalendarModule, MultiSelectModule, SliderModule, MenuModule, DialogModule, CheckboxModule, SharedModule } from 'primeng/primeng';
import { RestHandler, IRestRequest, IRestResponse } from 'rest-core';
import { RestHandlerHttp, RestModule } from 'rest-ngx-http';

import { ApiService, ConfigService, CorpusService, DownloadService, ElasticSearchService, HighlightService, ManualService, SearchService, SessionService, UserService, LogService, QueryService } from './services/index';

import { AppComponent } from './app.component';
import { CorpusSelectionComponent } from './corpus-selection/corpus-selection.component';
import { HomeComponent } from './home/home.component';
import { HighlightPipe, SearchComponent, SearchFilterComponent, SearchRelevanceComponent, SearchResultsComponent } from './search/index';
import { ManualDialogComponent } from './manual/manual-dialog.component';
import { MenuComponent } from './menu/menu.component';
import { CorpusGuard } from './corpus.guard';
import { LoggedOnGuard } from './logged-on.guard';
import { LoginComponent } from './login/login.component';
import { ScrollToDirective } from './scroll-to.directive';
import { BarChartComponent } from './visualization/barchart.component';
import { VisualizationComponent } from './visualization/visualization.component';
import { DocumentViewComponent } from './document-view/document-view.component';

const appRoutes: Routes = [
    {
        path: 'search/:corpus',
        component: SearchComponent,
        canActivate: [CorpusGuard, LoggedOnGuard]
    },
    {
        path: 'login',
        component: LoginComponent
    },
    {
        path: 'home',
        component: HomeComponent,
        canActivate: [LoggedOnGuard]
    },
    {
        path: '',
        redirectTo: 'home',
        pathMatch: 'full'
    }
]
@NgModule({
    declarations: [
        AppComponent,
        HomeComponent,
        CorpusSelectionComponent,
        HighlightPipe,
        SearchComponent,
        SearchFilterComponent,
        SearchResultsComponent,
        ManualDialogComponent,
        MenuComponent,
        LoginComponent,
        ScrollToDirective,
        BarChartComponent,
        VisualizationComponent,
        SearchRelevanceComponent,
        DocumentViewComponent
    ],
    imports: [
        BrowserAnimationsModule,
        BrowserModule,
        CalendarModule,
        CommonModule,
        FormsModule,
        HttpModule,
        RouterModule.forRoot(appRoutes),
        MarkdownModule,
        MultiSelectModule,
        SliderModule,
        MenuModule,
        DialogModule,
        CheckboxModule,
        SharedModule,
        RestModule.forRoot({
            handler: { provide: RestHandler, useFactory: (restHandlerFactory), deps: [Http] }
        })
    ],
    providers: [ApiService, CorpusService, ConfigService, DownloadService, ElasticSearchService, HighlightService, LogService, ManualService, QueryService, SearchService, SessionService, UserService, CorpusGuard, LoggedOnGuard],
    bootstrap: [AppComponent]
})
export class AppModule { }

// AoT requires an exported function for factories
export function restHandlerFactory(http: Http) {
    return new RestHandlerSession(http);
}

/**
 * Rest handler which will emit an event when the session expired.
 */
class RestHandlerSession extends RestHandlerHttp {
    constructor(http: Http) {
        super(http);
    }

    public handleResponse(req: IRestRequest, response: Response): IRestResponse {
        if (!response.ok && response.status == 401) {
            SessionService.markExpired();
        }

        return super.handleResponse(req, response);
    }
}
