import { of, Observable } from 'rxjs';

import { Corpus, NamedEntitiesResult } from '../app/models';

export class EntityServiceMock {

    public getDocumentEntities(corpus: Corpus, id: string): Observable<NamedEntitiesResult> {
        return of({annotations: [{'content': '<span class="entity-person">Wally</span> was last seen in <span class="entity-location">Paris</span>'}], entities: ['location', 'person']})   
    }
}
