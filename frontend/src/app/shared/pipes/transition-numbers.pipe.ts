import { ChangeDetectorRef, Inject, LOCALE_ID, Pipe, PipeTransform } from '@angular/core';
import { formatNumber } from '@angular/common';
import { animationFrames, map, takeWhile, endWith, Subscription, Observable } from 'rxjs';
import bezier from 'bezier-easing';

const animationTime = 200; // ms
const easing = bezier(0.00, 0.67, 0.41, 1);

@Pipe({
    name: 'transitionNumbers',
    pure: false,
    standalone: true
})
export class TransitionNumbersPipe implements PipeTransform {
    private current = 0;
    private target = 0;
    private subscription: Subscription = undefined;

    constructor(private ref: ChangeDetectorRef, @Inject(LOCALE_ID) private locale: string) {
    }

    /**
     * Transforms a number to smoothly transition between values.
     */
    transform(value?: number, transitionBackwards = true) {
        if (value === undefined || value === null) {
            if (this.subscription) {
                this.subscription.unsubscribe();
                delete this.subscription;
            }
            return '';
        }

        if (this.target !== value) {
            this.subscription?.unsubscribe();
            this.target = value;

            if (this.current == 0 || !transitionBackwards && this.current > this.target) {
                // don't animate the first jump after loading
                // jumping backwards?
                // (query was updated, don't animate this jump either)
                this.current = this.target;
            } else {
                this.subscription = transitionValue(this.current, this.target, animationTime, this.target).subscribe(
                    value => {
                        this.current = Math.round(value);
                        this.ref.markForCheck();
                    }
                );
            }
        }

        return formatNumber(this.current, this.locale);
    }
}

export function transitionValue<T = number>(start: number, end: number, duration: number, endWithOther?: T): Observable<number | T> {
    const diff = end - start;
    return animationFrames().pipe(
        // from 0 to 1
        map(({ elapsed }) => elapsed / duration),
        takeWhile(v => v < 1),
        endWith(endWithOther ?? end),
        map(v => v === endWithOther ? endWithOther : easing(<number>v) * diff + start)
    );
}
