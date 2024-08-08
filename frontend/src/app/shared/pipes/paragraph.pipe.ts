import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
    name: 'paragraph',
})
export class ParagraphPipe implements PipeTransform {

    transform(content: string | string[]): unknown {
        const splitText = this.addParagraphBreaks(content);
        return splitText;
    }

    addParagraphBreaks(content: string | string[]) {
        const paragraphs = typeof content === 'string' ? content.split('\n') : content;
        if (!paragraphs || paragraphs.length === 1) {
            return content;
        }
        return paragraphs.filter(p => p !== '').join('<br><br>');
    }


}
