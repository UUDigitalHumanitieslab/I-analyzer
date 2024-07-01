import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import * as _ from 'lodash';
import { combineLatest } from 'rxjs';
import { Corpus, FoundDocument } from '../models';
import { CorpusService, ElasticSearchService } from '../services';
import { makeContextParams } from '../utils/document-context';
import { documentIcons } from '../shared/icons';
import { Title } from '@angular/platform-browser';
import { pageTitle } from '../utils/app';

@Component({
  selector: 'ia-document-page',
  templateUrl: './document-page.component.html',
  styleUrls: ['./document-page.component.scss']
})
export class DocumentPageComponent implements OnInit {
    corpus: Corpus;
    documentId: string;
    document: FoundDocument;

    documentFound: boolean;

    documentIcons = documentIcons;

    showNEROption: boolean;

    showNamedEntities = false;

    constructor(
        private corpusService: CorpusService,
        private elasticSearchService: ElasticSearchService,
        private activatedRoute: ActivatedRoute,
        private title: Title,
    ) { }

    get contextDisplayName(): string {
        if (this.document?.hasContext) {
            return this.corpus.documentContext.displayName;
        }
    }

    get contextLink(): any {
        if (this.document && this.corpus) {
            return ['/search', this.corpus.name];
        }
    }

    get contextQueryParams(): any {
        if (this.document && this.corpus) {
            return makeContextParams(this.document, this.corpus);
        }
    }

    ngOnInit(): void {
        combineLatest([
            this.activatedRoute.params,
            this.corpusService.currentCorpus
        ]).subscribe(([params, corpus]) => {
            this.corpus = corpus;
            this.documentId = params['id'];
            this.showNEROption = this.corpus.hasNamedEntities;
            this.getDocument(this.documentId);
            this.title.setTitle(pageTitle(`Document in ${corpus.title}`));
        });
    }

    getDocument(id: string) {
        this.elasticSearchService.getDocumentById(id, this.corpus).then(document => {
            this.document = document;
            this.documentFound = !_.isUndefined(this.document);
        });
    }

    toggleNER(active: boolean): void {
        this.showNamedEntities = active;
    }


}
