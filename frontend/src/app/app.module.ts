import { APP_BASE_HREF, TitleCasePipe } from '@angular/common';
import { NgModule } from '@angular/core';

import { ExtraOptions, RouterModule, Routes } from '@angular/router';

import { CookieService } from 'ngx-cookie-service';
import { DialogModule } from 'primeng/dialog';
import { MenuModule } from 'primeng/menu';


import {
    ApiRetryService,
    ApiService,
    ElasticSearchService,
    HighlightService,
} from './services/index';

import { AboutComponent } from './about/about.component';
import { AppComponent } from './app.component';
import { CorpusDefinitionsModule } from './corpus-definitions/corpus-definitions.module';
import { CreateDefinitionComponent } from './corpus-definitions/create-definition/create-definition.component';
import { DefinitionsOverviewComponent } from './corpus-definitions/definitions-overview/definitions-overview.component';
import { DefinitionInOutComponent } from './corpus-definitions/definition-in-out/definition-in-out.component';
import { CorpusFormComponent } from './corpus-definitions/form/corpus-form/corpus-form.component';
import { FieldFormComponent } from './corpus-definitions/form/field-form/field-form.component';
import { MetaFormComponent } from './corpus-definitions/form/meta-form/meta-form.component';
import { CorpusModule } from './corpus-header/corpus.module';
import { CorpusInfoComponent } from './corpus-info/corpus-info.component';
import { CorpusSelectionModule } from './corpus-selection/corpus-selection.module';
import { CorpusGuard } from './corpus.guard';
import { DialogComponent } from './dialog/dialog.component';
import { DocumentPageComponent } from './document-page/document-page.component';
import { DocumentModule } from './document/document.module';
import { FooterComponent } from './footer/footer.component';
import { forwardLegacyParamsGuard } from './forward-legacy-params.guard';
import { DownloadHistoryComponent } from './history/download-history/download-history.component';
import { HistoryModule } from './history/history.module';
import { SearchHistoryComponent } from './history/search-history/index';
import { HomeComponent } from './home/home.component';
import { LoggedOnGuard } from './logged-on.guard';
import { LoginComponent } from './login/login.component';
import { LoginModule } from './login/login.module';
import { RegistrationComponent } from './login/registration/registration.component';
import { RequestResetComponent } from './login/reset-password/request-reset.component';
import { ResetPasswordComponent } from './login/reset-password/reset-password.component';
import { VerifyEmailComponent } from './login/verify-email/verify-email.component';
import { ManualComponent } from './manual/manual.component';
import { ManualModule } from './manual/manual.module';
import { MenuComponent } from './menu/menu.component';
import { NotificationsComponent } from './notifications/notifications.component';
import { PrivacyComponent } from './privacy/privacy.component';
import { SearchComponent } from './search/index';
import { SearchModule } from './search/search.module';
import { SettingsComponent } from './settings/settings.component';
import { SettingsModule } from './settings/settings.module';
import { SharedModule } from './shared/shared.module';
import { TagOverviewComponent } from './tag/tag-overview/tag-overview.component';
import { WordModelsComponent } from './word-models/word-models.component';
import { WordModelsModule } from './word-models/word-models.module';

export const appRoutes: Routes = [
    {
        path: 'search/:corpus',
        component: SearchComponent,
        canActivate: [CorpusGuard, forwardLegacyParamsGuard],
    },
    {
        path: 'word-models/:corpus',
        component: WordModelsComponent,
        canActivate: [CorpusGuard, forwardLegacyParamsGuard],
    },
    {
        path: 'info/:corpus',
        component: CorpusInfoComponent,
        canActivate: [CorpusGuard],
    },
    {
        path: 'document/:corpus/:id',
        component: DocumentPageComponent,
        canActivate: [CorpusGuard],
    },
    {
        path: 'login',
        component: LoginComponent,
    },
    {
        path: 'login/:activated',
        component: LoginComponent,
    },
    {
        path: 'registration',
        component: RegistrationComponent,
    },
    {
        path: 'reset',
        component: RequestResetComponent,
    },
    {
        path: 'reset-password/:uid/:token',
        component: ResetPasswordComponent,
    },
    {
        path: 'privacy',
        component: PrivacyComponent,
    },
    {
        path: 'home',
        component: HomeComponent,
    },
    {
        path: 'manual/:identifier',
        component: ManualComponent,
    },
    {
        path: 'about',
        component: AboutComponent,
    },
    {
        path: 'search-history',
        component: SearchHistoryComponent,
        canActivate: [LoggedOnGuard],
    },
    {
        path: 'download-history',
        component: DownloadHistoryComponent,
        canActivate: [LoggedOnGuard],
    },
    {
        path: 'confirm-email/:key',
        component: VerifyEmailComponent,
    },
    {
        path: 'settings',
        component: SettingsComponent,
        canActivate: [LoggedOnGuard],
    },
    {
        path: 'tags',
        component: TagOverviewComponent,
        canActivate: [LoggedOnGuard],
    },
    {
        path: 'corpus-definitions',
        canActivate: [LoggedOnGuard],
        children: [
            {
                path: 'new',
                component: CreateDefinitionComponent,
            },
            {
                path: 'io/:corpusID',
                component: DefinitionInOutComponent,
            },
            {
                path: 'edit/:corpusID',
                component: CorpusFormComponent,
            },
            {
                path: '',
                component: DefinitionsOverviewComponent,
            },
        ],
    },
    {
        path: '',
        redirectTo: 'home',
        pathMatch: 'full',
    },
];

const routerOptions: ExtraOptions = {
    scrollPositionRestoration: 'disabled',
    anchorScrolling: 'enabled',
};

export const declarations: any[] = [
    AppComponent,
    DialogComponent,
    FooterComponent,
    HomeComponent,
    MenuComponent,
    NotificationsComponent,
];

export const imports: any[] = [
    SharedModule,
    // Feature Modules
    CorpusModule,
    CorpusDefinitionsModule,
    CorpusSelectionModule,
    DialogModule,
    DocumentModule,
    HistoryModule,
    LoginModule,
    ManualModule,
    MenuModule,
    SearchModule,
    SettingsModule,
    WordModelsModule,
    RouterModule.forRoot(appRoutes, routerOptions),
];

export const providers: any[] = [
    ApiService,
    ApiRetryService,
    ElasticSearchService,
    HighlightService,
    CorpusGuard,
    LoggedOnGuard,
    TitleCasePipe,
    CookieService,
    { provide: APP_BASE_HREF, useValue: '/' },
];

@NgModule({
    declarations,
    imports,
    providers,
    bootstrap: [AppComponent],
})
export class AppModule {}
