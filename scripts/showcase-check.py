"""Verify the pinned project sequence with real scrolling, resizing and reduced motion."""
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
    page = browser.new_page(viewport={'width': 1480, 'height': 900})
    page.add_init_script("sessionStorage.setItem('leddisplay-intro-v3','1')")
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.goto('http://127.0.0.1:3000/', wait_until='networkidle')
    page.evaluate('document.documentElement.style.scrollBehavior="auto"')
    assert page.locator('.visual-caption').evaluate('(e)=>getComputedStyle(e).borderRightWidth') == '0px'
    assert page.locator('.showcase-card').count() == 4

    for width, height in [(1480, 900), (1159, 764), (1024, 600)]:
        page.set_viewport_size({'width': width, 'height': height})
        page.wait_for_timeout(250)
        metrics = page.evaluate('''()=>{
            const s=document.querySelector('.showcase-section'), header=document.querySelector('.header');
            return {start:s.getBoundingClientRect().top+scrollY-header.offsetHeight,
                top:header.offsetHeight,
                distance:s.querySelector('.showcase-grid').scrollWidth-s.querySelector('.showcase-viewport').clientWidth};
        }''')
        for index in [0, 1, 2, 3, 1]:
            page.evaluate('(y)=>scrollTo({top:y,behavior:"instant"})', metrics['start'] + metrics['distance'] * index / 3)
            page.wait_for_timeout(300)
            stage = page.locator('.showcase-stage').bounding_box()
            assert abs(stage['y'] - metrics['top']) < 2, (width, index, stage)
            viewport = page.locator('.showcase-viewport').bounding_box()
            card = page.locator('.showcase-card').nth(index).bounding_box()
            assert abs(card['x'] - viewport['x']) < 3, (width, index, card)
            assert abs(card['width'] - viewport['width']) < 2
            assert page.locator('[data-project-step][aria-current]').inner_text() == f'0{index+1}'
        before = page.locator('.showcase-stage').bounding_box()['y']
        page.mouse.move(width / 2, height / 2)
        page.mouse.wheel(0, 240)
        page.wait_for_timeout(350)
        assert abs(page.locator('.showcase-stage').bounding_box()['y'] - before) < 2
        controls = page.locator('.showcase-steps').bounding_box()
        whatsapp = page.locator('.whatsapp-floating').bounding_box()
        assert controls['x'] + controls['width'] < whatsapp['x']
        page.evaluate('(y)=>scrollTo({top:y,behavior:"instant"})', metrics['start'] + metrics['distance'] + 200)
        page.wait_for_timeout(250)
        assert page.locator('.showcase-stage').bounding_box()['y'] < metrics['top'] - 150
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')

    page.set_viewport_size({'width': 1480, 'height': 900})
    page.wait_for_timeout(250)
    page.locator('[data-project-step="2"]').evaluate('(e)=>e.click()')
    page.wait_for_timeout(1600)
    assert page.locator('[data-project-step][aria-current]').inner_text() == '03'
    page.locator('.showcase-card').nth(2).locator('.scene-open').click()
    assert page.locator('#application-gallery').is_visible()
    page.keyboard.press('Escape')
    assert not page.locator('#application-gallery').is_visible()

    for width, height, reduced in [(390, 844, 'no-preference'), (1480, 900, 'reduce'), (1024, 540, 'no-preference')]:
        page.set_viewport_size({'width': width, 'height': height})
        page.emulate_media(reduced_motion=reduced)
        page.wait_for_timeout(250)
        assert page.locator('.showcase-pinned').count() == 0
        assert page.locator('.showcase-section').evaluate('(e)=>e.style.height') == ''
        for card in page.locator('.showcase-card').all():
            assert card.bounding_box()['height'] > 250
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    assert not errors, errors
    browser.close()
    print('Project pinning, wheel scroll, reverse scroll, release, controls, gallery and responsive fallbacks passed.')
