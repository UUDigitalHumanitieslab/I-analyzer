import { NgModule } from '@angular/core';
import { SharedModule } from '../shared/shared.module';
import { ManualNavigationComponent } from './manual-navigation.component';
import { ManualComponent } from './manual.component';
import { AboutComponent } from '../about/about.component';
import { PrivacyComponent } from '../privacy/privacy.component';
import { RegexHighlightPipe } from '../shared/pipes';


@NgModule({
    declarations: [
        AboutComponent,
        ManualComponent,
        ManualNavigationComponent,
        PrivacyComponent,
        RegexHighlightPipe
    ],
    imports: [
        SharedModule
    ], exports: [
        AboutComponent,
        ManualComponent,
        PrivacyComponent,
    ]
})
export class ManualModule { }
