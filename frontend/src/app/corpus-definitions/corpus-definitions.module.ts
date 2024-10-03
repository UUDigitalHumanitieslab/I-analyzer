import { NgModule } from '@angular/core';
import { DefinitionsOverviewComponent } from './definitions-overview/definitions-overview.component';
import { SharedModule } from '@shared/shared.module';
import { CreateDefinitionComponent } from './create-definition/create-definition.component';
import { DefinitionInOutComponent } from './definition-in-out/definition-in-out.component';
import { DefinitionJsonUploadComponent } from './definition-json-upload/definition-json-upload.component';
import { ReactiveFormsModule } from '@angular/forms';
import { MetaFormComponent } from './form/meta-form/meta-form.component';
import { FieldFormComponent } from './form/field-form/field-form.component';
import { StepsModule } from 'primeng/steps';
import { CorpusFormComponent } from './form/corpus-form/corpus-form.component';
import { UploadSampleComponent } from './form/upload-sample/upload-sample.component';
import { MultiSelectModule } from 'primeng/multiselect';
import { DropdownModule } from 'primeng/dropdown';

@NgModule({
    declarations: [
        CreateDefinitionComponent,
        DefinitionsOverviewComponent,
        DefinitionInOutComponent,
        DefinitionJsonUploadComponent,
        MetaFormComponent,
        CorpusFormComponent,
        FieldFormComponent,
        UploadSampleComponent,
    ],
    exports: [
        CreateDefinitionComponent,
        DefinitionsOverviewComponent,
        DefinitionInOutComponent,
        CorpusFormComponent,
    ],
    imports: [
        SharedModule,
        ReactiveFormsModule,
        StepsModule,
        MultiSelectModule,
        DropdownModule,
    ],
})
export class CorpusDefinitionsModule {}
