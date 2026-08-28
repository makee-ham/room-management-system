from pathlib import Path

path = Path('.github/automation/qa-demo-date-all-maid-availability.mjs')
text = path.read_text(encoding='utf-8')
old = """    return { overflow, viewportWidth, scrollWidth: document.documentElement.scrollWidth, elements };
"""
new = """    const targetSelectors = [
      'html',
      'body',
      '#app',
      '#main-content',
      '.quick-booking-page',
      '.quick-grid-shell',
      '.quick-grid-status',
      '.quick-grid-mobile-header',
      '#quick-grid-scroller',
    ];
    const targets = targetSelectors.map(selector => {
      const element = document.querySelector(selector);
      if (!element) return { selector, missing: true };
      const rect = element.getBoundingClientRect();
      const style = getComputedStyle(element);
      return {
        selector,
        left: Math.round(rect.left * 10) / 10,
        right: Math.round(rect.right * 10) / 10,
        width: Math.round(rect.width * 10) / 10,
        scrollWidth: element.scrollWidth,
        clientWidth: element.clientWidth,
        offsetWidth: element.offsetWidth,
        overflowX: style.overflowX,
        overflowY: style.overflowY,
        boxSizing: style.boxSizing,
        boxShadow: style.boxShadow,
        maxWidth: style.maxWidth,
        minWidth: style.minWidth,
        contain: style.contain,
        position: style.position,
      };
    });
    return { overflow, viewportWidth, scrollWidth: document.documentElement.scrollWidth, elements, targets };
"""
if text.count(old) != 1:
    raise SystemExit(f'overflow report return marker mismatch: {text.count(old)}')
path.write_text(text.replace(old, new, 1), encoding='utf-8')
