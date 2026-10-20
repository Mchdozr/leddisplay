"""Exercise every new experience using real browser interactions and public source data."""
from pathlib import Path
from playwright.sync_api import sync_playwright
BASE='http://127.0.0.1:3000'
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    context=browser.new_context(viewport={'width':1480,'height':1000},reduced_motion='reduce')
    context.add_init_script("sessionStorage.setItem('leddisplay-intro-v3','1')")
    page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto(BASE+'/',wait_until='domcontentloaded')
    page.wait_for_selector('#size-result .size-result-heading')
    assert '120' in page.locator('#size-result').inner_text()
    assert '2560 × 1536' in page.locator('#size-result').inner_text()
    page.locator('#size-model').select_option('grand-air-ic-mekan-2.604-1000')
    page.locator('#size-width').fill('4');page.locator('#size-height').fill('3')
    page.get_by_role('button',name='Ekranı hesapla').click()
    page.wait_for_function("document.querySelector('#size-result').innerText.includes('1536 × 1152')")
    assert '24' in page.locator('#size-result').inner_text()
    quote=page.locator('#size-quote').get_attribute('href');page.locator('#size-quote').click()
    assert page.locator('input[name=products]:checked').count()==1
    assert '24 kabin' in page.locator('[name=message]').input_value()
    page.goto(BASE+'/',wait_until='domcontentloaded');page.wait_for_selector('#size-result .size-result-heading')
    page.locator('#size-width').fill('0.1');page.locator('#size-height').fill('0.1');page.locator('#size-fit').select_option('at-most')
    page.get_by_role('button',name='Ekranı hesapla').click();page.wait_for_selector('#size-error:not([hidden])')
    assert page.locator('#size-quote').is_hidden()
    page.locator('#pixel-tab').click();assert page.locator('#pixel-panel').is_visible();assert not page.locator('#size-panel').is_visible()
    before=page.locator('#pixel-canvas').evaluate('(e)=>e.toDataURL()')
    page.locator('[data-pixel-preset="5"]').click()
    after=page.locator('#pixel-canvas').evaluate('(e)=>e.toDataURL()');assert before!=after
    assert 'P10' in page.locator('#pixel-summary').inner_text()
    page.locator('#pixel-distance').fill('10');page.locator('#pixel-distance').dispatch_event('input')
    assert after!=page.locator('#pixel-canvas').evaluate('(e)=>e.toDataURL()')
    page.locator('#pixel-panel').screenshot(path='/workspace/leddisplay-piksel-deneyimi.png')
    page.locator('#pixel-tab').focus();page.keyboard.press('ArrowLeft')
    assert page.locator('#size-tab').get_attribute('aria-selected')=='true'
    # Click and scroll narratives are distinct; hotspot locations follow the contained image.
    page.locator('[data-story-select="0"]').click();page.locator('[data-hotspot="1"]').click()
    assert 'Kabin birleşimi' in page.locator('#hotspot-description').inner_text()
    page.locator('[data-hotspot="3"]').click();assert 'Güç ve veri' in page.locator('#hotspot-description').inner_text()
    for index in [1,2,0]:
        page.locator(f'[data-story-select="{index}"]').click()
        assert page.locator(f'[data-story-select="{index}"]').get_attribute('aria-pressed')=='true'
    page.locator('.product-story').screenshot(path='/workspace/leddisplay-deneyim-anlatim.png')
    # Native fullscreen gallery opens, changes via button and keyboard, and returns focus on Escape.
    page.locator('.scene-open').first.click();gallery=page.locator('#application-gallery');assert gallery.is_visible()
    assert '01 / 04' in gallery.inner_text();assert 'Tamamlanmış müşteri projesi' in gallery.inner_text()
    page.locator('#application-next').click();assert page.locator('#application-title').inner_text()=='Sahne & etkinlik'
    page.keyboard.press('ArrowRight');assert page.locator('#application-title').inner_text()=='Kurumsal & mimari'
    page.locator('#application-next').click();assert 'Şehrin' in page.locator('#application-title').inner_text()
    page.screenshot(path='/workspace/leddisplay-tam-ekran-galeri.png')
    page.keyboard.press('Escape');assert not gallery.is_visible();assert page.locator('.scene-open').first.evaluate('(e)=>e===document.activeElement')
    # Comparison, filtering, limit, persistence and transfer of all products to the contact form.
    page.goto(BASE+'/urunler',wait_until='domcontentloaded');page.wait_for_selector('[data-compare-id]:not([hidden])')
    ids=['h-1-25-ic-mekan','gob-1-86-ic-mekan','front-4-dis-mekan','esnek-1-86-ic-mekan']
    for slug in ids[:3]:page.locator(f'.catalog-grid [data-compare-id="{slug}"]').click()
    page.locator(f'.catalog-grid [data-compare-id="{ids[3]}"]').click();assert 'En fazla üç' in page.locator('#compare-status').inner_text()
    page.locator('#compare-open').click();dialog=page.locator('#compare-dialog');assert dialog.is_visible()
    count=page.locator('#compare-table tbody tr').count();assert count==10
    assert page.locator('#compare-table td').first.evaluate('(e)=>getComputedStyle(e).color')=='rgb(24, 51, 74)'
    page.locator('#compare-differences').check();assert 0<page.locator('#compare-table tbody tr').count()<count
    page.locator('#compare-differences').uncheck();assert page.locator('#compare-table tbody tr').count()==10
    page.screenshot(path='/workspace/leddisplay-urun-karsilastirma.png')
    page.locator('#compare-quote').click();assert page.locator('input[name=products]:checked').count()==3
    page.goto(BASE+'/urunler',wait_until='domcontentloaded');page.wait_for_selector('#compare-selection-count')
    assert '3 / 3' in page.locator('#compare-selection-count').inner_text()
    page.locator('#product-search').fill('H1.25 İç Mekân');assert page.locator('.catalog-product-shell:visible').count()==1
    page.locator('#product-search').fill('')
    # Real cross-document view transition; navigation still uses ordinary links.
    page.evaluate("addEventListener('pageswap',event=>sessionStorage.setItem('tested-page-transition',String(!!event.viewTransition)),{once:true})")
    page.locator('.catalog-grid .product-card[href="/urun-h-1-25-ic-mekan"]').click()
    assert page.url.endswith('/urun-h-1-25-ic-mekan')
    assert page.locator('#product-main-image').evaluate('(e)=>getComputedStyle(e).viewTransitionName')=='product-visual'
    # Reduced-motion intentionally skips effects; animation preference is verified below separately.
    page.goto(BASE+'/urun-grand-air-ic-mekan');page.locator('[data-detail-hotspot="2"]').click()
    assert 'Servis alanı' in page.locator('.point-detail').inner_text()
    # Responsive tools and dialogs. No clipping of document width.
    for width in [1024,768,390,360]:
        page.set_viewport_size({'width':width,'height':844});page.goto(BASE+'/',wait_until='domcontentloaded')
        page.wait_for_selector('#size-result .size-result-heading')
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),width
        page.locator('#pixel-tab').click();assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.locator('.scene-open').first.click();assert gallery.is_visible();assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.keyboard.press('Escape')
    page.set_viewport_size({'width':390,'height':844});page.locator('#ekran-planlayici').screenshot(path='/workspace/leddisplay-deneyim-mobil.png')
    # Live hero pauses, resumes, and switches to a real image. Scroll changes the sticky story.
    animated=browser.new_page(viewport={'width':1480,'height':1000},reduced_motion='no-preference')
    animated.add_init_script("sessionStorage.setItem('leddisplay-intro-v3','1')")
    animated.on('pageerror',lambda e:errors.append(str(e)));animated.goto(BASE+'/',wait_until='domcontentloaded')
    animated.wait_for_selector('.hero-motion-ready')
    first=animated.locator('#hero-motion').evaluate('(e)=>e.toDataURL()');animated.wait_for_timeout(200)
    assert first!=animated.locator('#hero-motion').evaluate('(e)=>e.toDataURL()')
    animated.locator('#hero-motion-toggle').click();first=animated.locator('#hero-motion').evaluate('(e)=>e.toDataURL()');animated.wait_for_timeout(150)
    assert first==animated.locator('#hero-motion').evaluate('(e)=>e.toDataURL()')
    animated.locator('#hero-scene-toggle').click();assert animated.locator('.hero-architecture>img').is_visible()
    for index in [0,1,2]:
        animated.locator(f'[data-story-step="{index}"]').evaluate("e=>e.scrollIntoView({block:'center',behavior:'instant'})")
        animated.wait_for_function(f"document.querySelector('[data-story-select=\"{index}\"]').getAttribute('aria-pressed')==='true'")
    animated.emulate_media(reduced_motion='reduce');animated.evaluate('scrollTo(0,0)');assert animated.locator('#hero-motion-toggle').get_attribute('aria-pressed')=='true'
    animated.emulate_media(reduced_motion='no-preference');animated.goto(BASE+'/urunler',wait_until='domcontentloaded')
    animated.evaluate("addEventListener('pageswap',event=>sessionStorage.setItem('tested-native-transition',String(!!event.viewTransition)),{once:true})")
    animated.locator('.catalog-grid .product-card[href="/urun-h-1-25-ic-mekan"]').click()
    if animated.evaluate("CSS.supports('view-transition-name: product-visual')"):
        assert animated.evaluate("sessionStorage.getItem('tested-native-transition')")=='true'
    nojs=browser.new_page(java_script_enabled=False,viewport={'width':390,'height':844});nojs.goto(BASE+'/')
    assert nojs.locator('h1').is_visible();assert nojs.locator('.corporate-hero-visual>img').is_visible();assert nojs.locator('.story-step').count()==3
    assert not errors,errors
    browser.close()
print('All eight experiences passed: live/paused hero, scroll story, hotspots, native navigation, three-product comparison, sizing/contact transfer, pitch simulator and keyboard/mobile fullscreen concept gallery. No external messages sent.')
