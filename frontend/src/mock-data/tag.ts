import { Observable, of } from 'rxjs';
import { Tag } from '../app/models';

export const mockTags: Tag[] = [
    {
        id: 1,
        name: 'fascinating',
        description: 'interesting documents',
        count: 2
    }, {
        id: 2,
        name: 'boring',
        description: 'useless documents',
        count: 1
    }
];

export class TagServiceMock {
    getDocumentTags(): Observable<Tag[]> {
        return of(mockTags);
    }
}
