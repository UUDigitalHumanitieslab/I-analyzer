import { NgModule } from '@angular/core';
import { SharedModule } from '../shared/shared.module';
import { DocumentViewComponent } from '../document-view/document-view.component';
import { DocumentPageComponent } from '../document-page/document-page.component';
import { ImageViewModule } from '../image-view/image-view.module';
import { SearchRelevanceComponent } from '../search';
import { CorpusModule } from '../corpus-header/corpus.module';
import { TagModule } from '../tag/tag.module';
import { DocumentPopupComponent } from './document-popup/document-popup.component';
import { DialogModule } from 'primeng/dialog';
import { DocumentPreviewComponent } from './document-preview/document-preview.component';
import { EntityLegendComponent } from './entity-legend/entity-legend.component';
import { EntityToggleComponent } from './entity-toggle/entity-toggle.component';
import { ElasticsearchHighlightPipe, GeoDataPipe, ParagraphPipe, SnippetPipe } from '../shared/pipes';

@NgModule({
    declarations: [
        DocumentViewComponent,
        DocumentPageComponent,
        SearchRelevanceComponent,
        DocumentPopupComponent,
        DocumentPreviewComponent,
        EntityLegendComponent,
        EntityToggleComponent,
        ElasticsearchHighlightPipe,
        GeoDataPipe,
        ParagraphPipe,
        SnippetPipe
    ],
    imports: [
        DialogModule,
        CorpusModule,
        SharedModule,
        ImageViewModule,
        TagModule,
    ], exports: [
        DocumentPreviewComponent,
        DocumentViewComponent,
        DocumentPageComponent,
        DocumentPopupComponent,
        EntityLegendComponent,
        EntityToggleComponent,
        SearchRelevanceComponent,
    ]
})
export class DocumentModule { }
