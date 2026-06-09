/**
 * Centralized JS override to support sequential lesson progress and automatic navigation.
 * Unlocks the next slide dynamically in the UI upon completion and redirects
 * students seamlessly without manual page refreshes.
 *
 * Dependencies:
 *   - @website_slides/js/slides_course_page
 *   - @website_slides/js/slides_course_fullscreen_player
 */

import { SlideCoursePage } from '@website_slides/js/slides_course_page';
import Fullscreen from '@website_slides/js/slides_course_fullscreen_player';

console.log("MY_ACADEMY: slides_course_page_override.js loaded and executing");

SlideCoursePage.include({
    /**
     * @override
     */
    async _toggleSlideCompleted(slide, completed = true) {
        console.log("MY_ACADEMY: SlideCoursePage._toggleSlideCompleted called for slide:", slide, "completed:", completed);
        const result = await this._super(...arguments);
        if (completed && slide) {
            // Check if we are NOT in the fullscreen player view
            const $allItems = $('.o_wslides_fs_sidebar_list_item');
            if ($allItems.length === 0) {
                console.log("MY_ACADEMY: Non-fullscreen view complete detected. Reloading page.");
                window.location.reload();
            }
        }
        return result;
    }
});

Fullscreen.include({
    /**
     * @override
     */
    async _toggleSlideCompleted(slide, completed = true) {
        console.log("MY_ACADEMY: Fullscreen._toggleSlideCompleted called for slide:", slide, "completed:", completed);
        const result = await this._super(...arguments);
        if (completed) {
            console.log("MY_ACADEMY: Fullscreen slide completed, triggering dynamic unlock.");
            this._unlockNextSlide();
        }
        return result;
    },

    /**
     * @override
     */
    init: function (parent, slides, defaultSlideId, channelData) {
        const result = this._super.apply(this, arguments);
        if (this.sidebar) {
            const self = this;
            this.sidebar._onClickTab = function (ev) {
                ev.stopPropagation();
                const $elem = $(ev.currentTarget).closest('.o_wslides_fs_sidebar_list_item');
                console.log("MY_ACADEMY: Overridden Sidebar._onClickTab called for element:", $elem);
                const canAccess = $elem.data('canAccess');
                if (canAccess === true || canAccess === 'True' || String(canAccess).toLowerCase() === 'true') {
                    const isQuiz = !!$elem.data('isQuiz');
                    const slideID = parseInt($elem.data('id'));
                    const slide = this.slideEntries.find(s => s.id === slideID && !!s.isQuiz === isQuiz);
                    console.log("MY_ACADEMY: Found slide in slideEntries:", slide);
                    if (slide) {
                        this._updateSlideEntry(slide);
                    } else {
                        console.log("MY_ACADEMY: Slide not found in slideEntries!");
                    }
                } else {
                    console.log("MY_ACADEMY: canAccess is not True/true", canAccess);
                }
            };
        }
        return result;
    },

    /**
     * @override
     */
    _onSlideGoToNext(ev) {
        const currentSlide = this._slideValue;
        console.log("MY_ACADEMY: Fullscreen._onSlideGoToNext called for current slide:", currentSlide);
        if (currentSlide) {
            // Case 1: If current is a slide (not quiz) and it has a quiz, go to its quiz first
            if (!currentSlide.isQuiz && currentSlide.hasQuestion) {
                const url = `/slides/slide/${currentSlide.slug}?fullscreen=1&quiz=1`;
                console.log("MY_ACADEMY: Navigating to quiz of current slide:", url);
                window.location.href = url;
                return;
            }

            // Case 2: Otherwise, find all slide items in the sidebar.
            const $allItems = $('.o_wslides_fs_sidebar_list_item[data-is-quiz!="1"]');
            console.log("MY_ACADEMY: Found non-quiz sidebar items:", $allItems.length);
            if ($allItems.length > 0) {
                const $currentEl = $allItems.filter(`[data-id="${currentSlide.id}"]`);
                const currentIndex = $allItems.index($currentEl);
                console.log("MY_ACADEMY: Current slide index in sidebar list:", currentIndex);
                if (currentIndex !== -1 && currentIndex < $allItems.length - 1) {
                    const $nextEl = $allItems.eq(currentIndex + 1);
                    const nextSlug = $nextEl.data('slug');
                    if (nextSlug) {
                        const url = `/slides/slide/${nextSlug}?fullscreen=1`;
                        console.log("MY_ACADEMY: Navigating to next slide:", url);
                        window.location.href = url;
                        return;
                    }
                }
            }
        }
        this._super(...arguments);
    },

    /**
     * Dynamically unlocks the next slide in the fullscreen player sidebar DOM
     * and updates the widget's slide lists to allow seamless navigation.
     */
    _unlockNextSlide() {
        const $allItems = $('.o_wslides_fs_sidebar_list_item');
        const currentSlide = this._slideValue;
        console.log("MY_ACADEMY: _unlockNextSlide execution start. currentSlide:", currentSlide, "sidebar items count:", $allItems.length);
        if (!currentSlide || $allItems.length === 0) {
            return;
        }

        const selector = currentSlide.isQuiz
            ? `[data-id="${currentSlide.id}"][data-is-quiz="1"]`
            : `[data-id="${currentSlide.id}"][data-is-quiz!="1"]`;
        const $currentEl = $allItems.filter(selector);
        const currentIndex = $allItems.index($currentEl);

        console.log("MY_ACADEMY: Selector used to find current element:", selector);
        console.log("MY_ACADEMY: Found current element in DOM:", $currentEl.length, "at index:", currentIndex);

        if (currentIndex !== -1 && currentIndex < $allItems.length - 1) {
            const $nextEl = $allItems.eq(currentIndex + 1);
            console.log("MY_ACADEMY: Next element found in DOM:", $nextEl.length, "data-id:", $nextEl.data('id'), "data-can-access:", $nextEl.data('canAccess'));
            if ($nextEl.data('canAccess') !== 'True') {
                console.log("MY_ACADEMY: Unlocking next element dynamically.");
                // 1. Mark as accessible in data and attributes
                $nextEl.data('canAccess', 'True');
                $nextEl.attr('data-can-access', 'True');

                // 2. Remove text-muting styling classes
                $nextEl.find('.text-600').removeClass('text-600');

                // 3. Replace lock icon/span with the standard play/quiz icon/button
                const $lockSpan = $nextEl.find('.o_wslides_sidebar_done_button span:has(.fa-lock)');
                console.log("MY_ACADEMY: Found lock span to replace:", $lockSpan.length);
                if ($lockSpan.length > 0) {
                    const isNextQuiz = $nextEl.data('isQuiz') === 1;
                    const iconClass = isNextQuiz ? 'fa-flag-checkered text-warning' : 'fa-circle-thin';
                    const $newButton = $('<button>', {
                        class: 'o_wslides_button_complete btn btn-sm',
                        html: $('<i>', { class: `fa ${iconClass} fa-fw fa-lg`, 'data-slide-id': $nextEl.data('id') })
                    });
                    $lockSpan.replaceWith($newButton);
                    console.log("MY_ACADEMY: Replaced lock span with unlocked completion button.");
                }

                // 4. If the title link was rendered as a span, replace it with an anchor link 'a'
                const $spanLink = $nextEl.find('span.d-block');
                console.log("MY_ACADEMY: Found span link to replace:", $spanLink.length);
                if ($spanLink.length > 0) {
                    const $aLink = $('<a>', {
                        class: 'd-block',
                        href: '#'
                    }).append($spanLink.contents());
                    $spanLink.replaceWith($aLink);
                    console.log("MY_ACADEMY: Replaced span title with anchor link.");
                }

                // 5. Update the slides arrays in memory to include the newly unlocked item
                const nextSlideData = $nextEl.data();
                const alreadyExists = this.slides.some(s => s.id === nextSlideData.id && s.isQuiz === !!nextSlideData.isQuiz);
                console.log("MY_ACADEMY: Next slide already exists in widget slides array?", alreadyExists);
                if (!alreadyExists) {
                    this.slides.length = 0;
                    const self = this;
                    const unlockedSlides = [];
                    $allItems.each(function () {
                        const $el = $(this);
                        if ($el.data('canAccess') === 'True') {
                            unlockedSlides.push($el.data());
                        }
                    });
                    const preprocessedList = this._preprocessSlideData(unlockedSlides);
                    preprocessedList.forEach(s => self.slides.push(s));
                    console.log("MY_ACADEMY: Rebuilt widget slides array. New count:", this.slides.length);

                    if (this.sidebar) {
                        this.sidebar.slideEntries = this.slides;
                        console.log("MY_ACADEMY: Updated sidebar slideEntries reference.");
                    }
                }
            }
        }
    }
});
