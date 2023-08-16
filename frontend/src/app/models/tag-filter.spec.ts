import { Tag } from './tag';
import { TagFilter } from './tag-filter';

describe('TagFilter', () => {
    let tags: Tag[];
    let filter: TagFilter;

    beforeEach(() => {
        tags = [
            {
                id: 1,
                name: 'great documents',
                description: '',
                count: 0,
            }, {
                id: 2,
                name: 'awful documents',
                description: '',
                count: 0,
            }
        ];
        filter = new TagFilter(tags);
    });

    it('should create', () => {
        expect(filter).toBeTruthy();
    });

    it('should convert to a string', () => {
        const data = [tags[1]];
        expect(filter.dataFromString(filter.dataToString(data))).toEqual(data);
    });
});
