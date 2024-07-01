import { CommonModule } from '@angular/common';
import { HttpClientModule, HttpClientXsrfModule } from '@angular/common/http';
import { NgModule } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { RouterModule } from '@angular/router';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { CalendarModule } from 'primeng/calendar';
import { TableModule } from 'primeng/table';
import { BalloonDirective } from '../balloon.directive';
import { DatePickerComponent } from '../corpus-selection/corpus-filter/date-picker/date-picker.component';
import { ErrorComponent } from '../error/error.component';
import { ScrollToDirective } from '../scroll-to.directive';
import { DropdownModule } from './dropdown/dropdown.module';
import { TabPanelDirective } from './tabs/tab-panel.directive';
import { TabsComponent } from './tabs/tabs.component';
import { ToggleComponent } from './toggle/toggle.component';
import { SlugifyPipe } from './pipes/slugify.pipe';

@NgModule({
    declarations: [
        DatePickerComponent,
        ErrorComponent,
        BalloonDirective,
        ScrollToDirective,
        TabsComponent,
        TabPanelDirective,
        ToggleComponent,
        SlugifyPipe,
    ],
    exports: [
        // shared components
        DatePickerComponent,
        ErrorComponent,
        ScrollToDirective,
        TabsComponent,
        TabPanelDirective,

        // shared modules
        BrowserAnimationsModule,
        BrowserModule,
        CommonModule,
        DropdownModule,
        FormsModule,
        FontAwesomeModule,
        BalloonDirective,
        HttpClientModule,
        HttpClientXsrfModule,
        RouterModule,
        TableModule,
        ToggleComponent,

        // Shared pipes
        SlugifyPipe,
    ],
    imports: [
        BrowserAnimationsModule,
        BrowserModule,
        CommonModule,
        FormsModule,
        CalendarModule,
        TableModule,
        DropdownModule,
        FontAwesomeModule,
        HttpClientModule,
        HttpClientXsrfModule.withOptions({
            cookieName: 'csrftoken',
            headerName: 'X-CSRFToken',
        }),
        RouterModule,
    ],
    providers: [SlugifyPipe],
})
export class SharedModule {}
