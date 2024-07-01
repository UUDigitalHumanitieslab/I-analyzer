import { maxSnippetsLength, HighlightService, TextPart } from './highlight.service';
import { omissionString } from './index';

describe('HighlightService', () => {
    let highlightService: HighlightService;
    beforeEach((() => {
        highlightService = new HighlightService();
    }));

    it('Works when there are no matches', () => {
        expectHighlights(
            'Certainly my troops must consist of numbers, or they can have no existence at all.',
            'letters',
            []);
    });

    it('Finds one match', () => {
        expectHighlights(
            'Certainly my troops must consist of numbers, or they can have no existence at all.',
            'numbers',
            [[36, 'numbers']]);
    });

    it('Finds multiple matches', () => {
        expectHighlights(
            'Sometimes it is the people no one can imagine anything of who do the things no one can imagine.',
            'imagine',
            [[38, 'imagine'],
            [87, 'imagine']]);
    });

    it('Accepts multiple', () => {
        const separators = ['', '+', '|'];
        for (const separator of separators) {
            expectHighlights(
                'Sometimes it is the people no one can imagine anything of who do the things no one can imagine.',
                `imagine ${separator} anything`,
                [[38, 'imagine'],
                [46, 'anything'],
                [87, 'imagine']]);
        }
    });

    it('Accepts quotes', () => {
        expectHighlights(
            'Sometimes it is the people no one can imagine anything of who do the things no one can imagine.',
            '"imagine anything"',
            [[38, 'imagine anything']]);

        // test surrogate pairs
        expectHighlights(
            '𝐀 💩 𝐁 I ♡ Unicode!',
            '"💩 𝐁"',
            [[2, '💩 𝐁']]);
    });

    it('Should only match fully', () => {
        expectHighlights(
            'pen apple pineapple',
            'apple',
            [[4, 'apple']]);
    });

    it('Accepts numbers', () => {
        expectHighlights(42, '', []);
        expectHighlights(123456, '23', []);
        expectHighlights(123, '123', [[0, '123']]);
    });

    it('Should accept wildcards', () => {
        expectHighlights(
            'They told me computers could only do arithmetic.',
            'co*',
            [[13, 'computers'],
            [23, 'could']]);
    });

    it('Should understand non-ASCII word boundaries', () => {
        expectHighlights(
            'Ik heb getwijfeld over België. Omdat iedereen daar lacht.',
            'België',
            [[23, 'België']]);
    });

    it('Should accept right-to-left text', () => {
        expectHighlights(
            'كتاب المختصر في حساب الجبر والمقابلة',
            'في كتاب',
            [[0, 'كتاب'],
            [13, 'في']]);
    });

    it('Should highlight multiline text', () => {
        expectHighlights(
            // eslint-disable-next-line max-len
            `I used to steal up there by myself (indeed I still do it in dreams) and sit conducting a little worship service of my own, adoring the chemical elements.
Here were the warp and woof of the world, a world that was later to expand into a Universe.
 -- Cecilia Payne-Gaposchkin`,
            'world Cecilia',
            [
                [189, 'world'],
                [198, 'world'],
                [250, 'Cecilia'],
            ]
        );
    });

    const expectHighlights = (value: string | number, query: string, expectedHighlightRanges: [number, string][]) => {
        const text = `${value}`;
        const highlights = highlightService.highlight(
            value,
            query);
        const expectedHighlights = getExpectedHighlights(new UnicodeString(text), expectedHighlightRanges);
        expect(getHighlightedString(highlights)).toEqual(getHighlightedString(expectedHighlights));
    };

    /**
     * Generates a sequence of numbers padded to 4 characters separated by spaces.
     *
     * @param start The starting number, inclusive
     * @param end The last number exclusive
     */
    const generateSequence = (start: number, end: number) => Array.from((function* () {
            for (let i = start; i < end; i++) {
                yield ('0000' + i).slice(-4);
            }
        })()).join(' ');

    const getExpectedHighlights = (text: UnicodeString, expectedHighlightRanges: [number, string][]) => {
        if (!expectedHighlightRanges.length) {
            return [{ substring: text.toString(), isHit: false }];
        }

        const expectedHighlights: TextPart[] = [];
        let lastIndex = 0;

        for (const range of expectedHighlightRanges) {
            const expectedHitPosition = range[0];
            if (expectedHitPosition > lastIndex) {
                expectedHighlights.push({ substring: text.substring(lastIndex, expectedHitPosition).toString(), isHit: false });
            }

            const expectedHitText = new UnicodeString(range[1]);
            expectedHighlights.push({ substring: text.substr(expectedHitPosition, expectedHitText.length).toString(), isHit: true });
            lastIndex = expectedHitPosition + expectedHitText.length;
        }

        if (text.length > lastIndex) {
            expectedHighlights.push({ substring: text.substring(lastIndex).toString(), isHit: false });
        }

        return expectedHighlights;
    };

    const getHighlightedString = (parts: Iterable<TextPart>) =>
        Array.from(parts).map(part => part.isHit ? `*${part.substring}*` : part.substring).join('');
});

/**
 * Wrapper for abstracting away Javascript unicode string handling oddities.
 */
class UnicodeString {
    private characters: string[];

    constructor(public value: string) {
        this.characters = Array.from(value);
    }

    public get length() {
        return this.characters.length;
    }

    public toString() {
        return this.value;
    }

    public substr(from: number, length?: number): UnicodeString {
        return this.substring(from, length ? from + length : undefined);
    }

    public substring(start: number, end?: number): UnicodeString {
        return new UnicodeString(this.characters.slice(start, end ? end : undefined).join(''));
    }
}
