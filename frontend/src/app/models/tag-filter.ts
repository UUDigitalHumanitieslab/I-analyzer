import { BaseFilter } from './base-filter';
import { Tag } from './tag';

export class TagFilter extends BaseFilter<void, Tag[]> {
    description = 'Show only results with these tags';
    filterType = 'TagFilter';
    routeParamName = 'tags';

    constructor(private userTags: Tag[]) {
        super();
    }

    makeDefaultData(parameters: void): Tag[] {
        return [];
    }

    dataToString(data: Tag[]): string {
        return data.map(tag => tag.id).join(',');
    }

    dataFromString(value: string): Tag[] {
        const ids = value.split(',');
        return this.userTags.filter(tag => ids.includes(tag.id.toString()));
    }
}
