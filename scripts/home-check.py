"""Exercise the homepage's commercial navigation, filters and solution finder."""
from pathlib import Path
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
    page = browser.new_page(viewport={'width': 1440, 'height': 1000}, reduced_motion='reduce')
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.goto('http://127.0.0.1:3000/', wait_until='networkidle')
    assert page.locator('.home-section').count() == 12
    assert page.locator('.featured-product:visible').count() == 8
    page.get_by_role('button', name='Dış mekân', exact=True).click()
    assert page.locator('.featured-product:visible').count() == 3
    page.get_by_role('button', name='Kiralık & esnek', exact=True).click()
    assert page.locator('.featured-product:visible').count() == 2
    page.get_by_role('button', name='Öne çıkanlar', exact=True).click()
    assert page.locator('.featured-product:visible').count() == 8
    page.locator('#solution-finder [name=place]').select_option('outdoor')
    page.locator('#solution-finder [name=project]').select_option('rental')
    assert page.locator('#finder-link').get_attribute('href') == '/urun-grand-air-dis-mekan.html'
    page.locator('#solution-finder [name=project]').select_option('curved')
    assert 'Dış mekânda' in page.locator('#finder-description').inner_text()
    assert page.locator('#finder-link').get_attribute('href') == '/ozel-led-cozumleri.html'
    for place in ['indoor', 'outdoor']:
        for project in ['fixed', 'rental', 'curved']:
            page.locator('#solution-finder [name=place]').select_option(place)
            page.locator('#solution-finder [name=project]').select_option(project)
            expected = ('/ozel-led-cozumleri.html' if project == 'curved' else
                        '/urun-grand-air-' + ('dis' if place == 'outdoor' else 'ic') + '-mekan.html' if project == 'rental' else
                        '/dis-mekan-led-ekran.html' if place == 'outdoor' else '/ic-mekan-led-ekran.html')
            assert page.locator('#finder-link').get_attribute('href') == expected
    page.locator('#solution-finder [name=place]').select_option('indoor')
    page.locator('#solution-finder [name=project]').select_option('fixed')
    page.locator('.support-topic summary').nth(1).click()
    assert page.locator('.support-topic').nth(1).get_attribute('open') is not None
    page.locator('.support-topic summary').nth(1).click()
    page.locator('.home-faq summary').first.click()
    assert page.locator('.home-faq details').first.get_attribute('open') is not None
    for width in [1440, 1024, 768, 390, 360]:
        page.set_viewport_size({'width': width, 'height': 900})
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), f'Overflow at {width}'
    page.locator('.home-faq summary').first.click()
    page.set_viewport_size({'width': 1440, 'height': 1000})
    page.locator('img').evaluate_all("images => images.forEach(image => image.loading = 'eager')")
    page.wait_for_function('Array.from(document.images).every(image => image.complete && image.naturalWidth > 0)')
    page.evaluate('window.scrollTo(0, 1500)')
    page.wait_for_function("document.querySelector('.back-to-top').classList.contains('is-visible')")
    assert page.locator('.reading-progress>span').evaluate('(e)=>getComputedStyle(e).transform') != 'matrix(0, 0, 0, 1, 0, 0)'
    page.get_by_role('link', name='Sayfanın başına dön').click()
    page.wait_for_function('scrollY < 150')
    assert page.locator('[data-entry-motion]').count() > 20
    assert page.locator('[data-entry-motion]').evaluate_all('items=>items.every(e=>e.getAnimations().length===0)')
    page.evaluate('window.scrollTo(0,0)')
    page.screenshot(path='/workspace/leddisplay-onizleme.png', full_page=True)
    page.screenshot(path='/workspace/leddisplay-hero-onizleme.png')
    page.set_viewport_size({'width': 390, 'height': 844})
    page.screenshot(path='/workspace/leddisplay-mobil-onizleme.png', full_page=True)
    # Normal-motion entry effects complete and respond to an accessibility preference change.
    animated = browser.new_page(viewport={'width': 1440, 'height': 1000}, reduced_motion='no-preference')
    animated.goto('http://127.0.0.1:3000/', wait_until='networkidle')
    animated.locator('.series-card').first.scroll_into_view_if_needed()
    animated.wait_for_function("document.querySelector('.series-card').classList.contains('motion-seen')")
    animated.emulate_media(reduced_motion='reduce')
    animated.wait_for_function("Array.from(document.querySelectorAll('[data-entry-motion]')).every(e=>e.getAnimations().length===0)")
    assert animated.locator('.series-card').first.is_visible()
    nojs = browser.new_context(java_script_enabled=False).new_page()
    nojs.goto('http://127.0.0.1:3000/')
    assert nojs.locator('.series-card').count() == 4
    assert nojs.locator('.readiness-checklist').is_visible()
    assert not errors, errors
    browser.close()
    print('Homepage: 8-product filters, 6 finder combinations, support accordion, scroll controls, reduced motion, no-JS content and 5 responsive widths passed.')
