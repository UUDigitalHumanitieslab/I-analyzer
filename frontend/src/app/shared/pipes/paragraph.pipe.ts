import { Pipe, PipeTransform } from '@angular/core';


@Pipe({
    name: 'paragraph',
})
export class ParagraphPipe implements PipeTransform {

    transform(content: string | string[]): unknown {
        const splitText = this.addParagraphTags(content);
        return splitText;
    }

    addParagraphTags(content: string | string[]) {
        const paragraphs = typeof content === 'string' ? content.split('\n') : content;
        if (paragraphs.length == 1) {
            return content;
        }
        return paragraphs.map(p => `<p>${p}</p>`).join(' ');
    }


}
