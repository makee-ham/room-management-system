from pathlib import Path

path = Path('.github/automation/qa-demo-date-all-maid-availability.mjs')
text = path.read_text(encoding='utf-8')
old = """    return { overflow, viewportWidth, scrollWidth: document.documentElement.scrollWidth, elements };
"""
new = """    const metric = (element, selector) => {
      if (!element) return { selector, missing: true };
      const rect = element.getBoundingClientRect();
      const style = getComputedStyle(element);
      return {
        selector,
        tag: element.tagName.toLowerCase(),
        id: element.id || '',
        className: typeof element.className === 'string' ? element.className : '',
        left: Math.round(rect.left * 10) / 10,
        right: Math.round(rect.right * 10) / 10,
        width: Math.round(rect.width * 10) / 10,
        scrollWidth: element.scrollWidth,
        clientWidth: element.clientWidth,
        offsetWidth: element.offsetWidth,
        overflowDelta: element.scrollWidth - element.clientWidth,
        overflowX: style.overflowX,
        overflowY: style.overflowY,
        display: style.display,
        gridTemplateColumns: style.gridTemplateColumns,
        flexDirection: style.flexDirection,
        boxSizing: style.boxSizing,
        boxShadow: style.boxShadow,
        maxWidth: style.maxWidth,
        minWidth: style.minWidth,
        contain: style.contain,
        position: style.position,
        paddingLeft: style.paddingLeft,
        paddingRight: style.paddingRight,
      };
    };
    const targetSelectors = [
      'html',
      'body',
      '#app',
      '#main-content',
      '.quick-booking-page',
      '.quick-booking-hero',
      '.quick-booking-toolbar',
      '.quick-month-tools',
      '.quick-booking-summary',
      '.quick-booking-guide',
      '.quick-booking-legend',
      '.quick-grid-shell',
      '.quick-grid-status',
      '.quick-grid-mobile-header',
      '#quick-grid-scroller',
    ];
    const targets = targetSelectors.map(selector => metric(document.querySelector(selector), selector));
    const quickPage = document.querySelector('.quick-booking-page');
    const directChildren = quickPage
      ? [...quickPage.children].map((element, index) => metric(element, `.quick-booking-page > :nth-child(${index + 1})`))
      : [];
    const smallOverflowContainers = [...document.querySelectorAll('body *')]
      .filter(element => {
        const delta = element.scrollWidth - element.clientWidth;
        return delta > 1 && delta <= 100;
      })
      .map((element, index) => metric(element, `small-overflow-${index + 1}`))
      .sort((left, right) => right.overflowDelta - left.overflowDelta)
      .slice(0, 30);
    return { overflow, viewportWidth, scrollWidth: document.documentElement.scrollWidth, elements, targets, directChildren, smallOverflowContainers };
"""
if text.count(old) != 1:
    raise SystemExit(f'overflow report return marker mismatch: {text.count(old)}')
path.write_text(text.replace(old, new, 1), encoding='utf-8')
