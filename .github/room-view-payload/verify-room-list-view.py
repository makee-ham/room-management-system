from pathlib import Path
from playwright.sync_api import sync_playwright

URL='http://127.0.0.1:4173/index.html'
OUT=Path('/tmp/room-list-view-qa')
OUT.mkdir(parents=True, exist_ok=True)

with sync_playwright() as p:
    browser=p.chromium.launch(headless=True)
    for width,height in [(1440,1000),(768,1000),(390,1200),(320,1200)]:
        page=browser.new_page(viewport={'width':width,'height':height})
        logs=[]
        page.on('console', lambda msg, logs=logs: logs.append(f'{msg.type}: {msg.text}') if msg.type in ('error','warning') else None)
        page.goto(URL, wait_until='load')
        assert 'CASTLE THE ART' in page.title(), page.title()
        assert page.locator('body').inner_text().strip(), 'blank page'
        page.evaluate("window.__CASTLE_TEST__.setRoomView('list')")
        page.wait_for_timeout(120)
        assert page.locator('text=객실 현황').count() >= 1

        state=page.evaluate("window.__CASTLE_TEST__.roomViewState()")
        assert state['view']=='list', state
        assert state['listCount']==121 and state['cardCount']==0, state
        assert page.get_attribute('[data-action="set-room-view"][data-view="list"]','aria-pressed')=='true'

        if width>=981:
            assert state['pinHeader']=='PIN 관리', state
            headers=[text.strip() for text in page.locator('.room-list-header span').all_inner_texts()]
            assert headers[-1]=='PIN 관리' and '관리' not in headers, headers
            widths=page.eval_on_selector_all('.room-list-item:first-of-type .room-list-actions .btn','els=>els.map(e=>e.getBoundingClientRect().width)')
            assert len(widths)==4 and max(widths)-min(widths)<=1, widths
            page.click('.room-list-item:first-of-type [data-action="pin-show"]')
            page.wait_for_timeout(80)
            pin=page.inner_text('.room-list-item:first-of-type .room-list-pin-copy strong')
            assert pin!='••••' and len(pin)==4, pin
            page.click('.room-list-item:first-of-type [data-action="pin-hide"]')
            assert page.inner_text('.room-list-item:first-of-type .room-list-pin-copy strong')=='••••'

        search=page.locator('#room-search')
        search.fill('350')
        page.wait_for_timeout(100)
        filtered=page.evaluate("window.__CASTLE_TEST__.roomViewState()")
        assert filtered['view']=='list' and filtered['listCount']==1 and filtered['cardCount']==0, filtered
        search.fill('')
        page.wait_for_timeout(100)
        assert page.evaluate("window.__CASTLE_TEST__.roomViewState().listCount")==121

        overflow=page.evaluate('document.documentElement.scrollWidth-document.documentElement.clientWidth')
        assert overflow<=0, (width,overflow)
        page.screenshot(path=str(OUT/f'list-{width}.png'), full_page=False)

        page.click('[data-action="set-room-view"][data-view="card"]')
        page.wait_for_timeout(100)
        card=page.evaluate("window.__CASTLE_TEST__.roomViewState()")
        assert card['view']=='card' and card['cardCount']==121 and card['listCount']==0, card
        assert page.get_attribute('[data-action="set-room-view"][data-view="card"]','aria-pressed')=='true'
        assert page.evaluate('document.documentElement.scrollWidth-document.documentElement.clientWidth')<=0
        if width in (1440,390):
            page.screenshot(path=str(OUT/f'card-{width}.png'), full_page=False)

        page.click('[data-action="set-room-view"][data-view="list"]')
        page.wait_for_timeout(100)
        restored=page.evaluate("window.__CASTLE_TEST__.roomViewState()")
        assert restored['view']=='list' and restored['listCount']==121, restored
        assert page.get_attribute('[data-action="set-room-view"][data-view="list"]','aria-pressed')=='true'
        assert not logs, logs
        page.close()
    browser.close()

print('Room card/list rendered QA passed')
