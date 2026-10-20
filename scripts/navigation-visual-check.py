"""Validate clean routes, real product images, hover previews and the one-time brand opener."""
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
BASE='http://127.0.0.1:3000'
solutions=['ic-mekan-led-ekran','dis-mekan-led-ekran','kiralik-led-ekran','ozel-led-cozumleri','led-video-wall']
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    context=browser.new_context(viewport={'width':1480,'height':900},reduced_motion='reduce')
    page=context.new_page();errors=[];page.on('pageerror',lambda error:errors.append(str(error)))
    for path in sorted(ROOT.glob('*.html')):
        slug=path.stem;target='/' if slug=='index' else '/'+slug
        response=page.goto(BASE+'/'+path.name+'?probe=preserved')
        assert response.status==200
        assert page.url==BASE+target+'?probe=preserved',page.url
        assert response.request.redirected_from.response().status==301
        assert page.locator('link[rel=canonical]').get_attribute('href')=='https://leddisplay.com.tr'+target
        assert page.locator('a[href*=".html"]').count()==0
    for width in [1480,1159,1024,768,390,360]:
        page.set_viewport_size({'width':width,'height':900})
        for slug in solutions+['urunler']:
            response=page.goto(BASE+'/'+slug)
            assert response.status==200
            page.locator('main img').first.scroll_into_view_if_needed()
            page.wait_for_function("[...document.querySelectorAll('main img')].filter(e=>e.getBoundingClientRect().top<innerHeight).every(e=>e.complete&&e.naturalWidth>0)")
            assert page.locator('main img').count()>0,slug
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(width,slug)
    page.set_viewport_size({'width':1480,'height':900});page.goto(BASE+'/')
    assert page.locator('.brand-intro').count()==0
    page.locator('.nav-product-group').hover()
    assert page.locator('#product-megamenu').is_visible()
    links=page.locator('.mega-product');assert links.count()==31
    for link in links.all():
        link.hover()
        assert page.locator('#product-megamenu').is_visible()
        assert page.locator('#mega-preview-title').inner_text()==link.get_attribute('data-preview-title')
        assert page.locator('#mega-preview-link').get_attribute('href')==link.get_attribute('href') or page.locator('#mega-preview-link').get_attribute('href')==BASE+link.get_attribute('href')
        image=page.locator('#mega-preview-image')
        if link.get_attribute('data-preview-image'):
            assert image.is_visible()
            assert image.get_attribute('src')==link.get_attribute('data-preview-image')
            page.wait_for_function("document.querySelector('#mega-preview-image').complete&&document.querySelector('#mega-preview-image').naturalWidth>0")
        else:assert page.locator('#mega-preview-unavailable').is_visible()
    page.locator('.mega-product[href="/urun-q-air-2-604-ic-mekan"]').hover()
    page.screenshot(path='/workspace/leddisplay-yeni-menu.png')
    page.locator('#mega-preview-link').hover();page.wait_for_timeout(300)
    assert page.locator('#product-megamenu').is_visible()
    page.keyboard.press('Escape');assert not page.locator('#product-megamenu').is_visible()
    page.locator('.product-menu-toggle').click();links.first.focus()
    assert page.locator('#mega-preview-title').inner_text()==links.first.get_attribute('data-preview-title')
    page.keyboard.press('Escape')
    page.set_viewport_size({'width':390,'height':844})
    page.get_by_role('button',name='Menüyü aç',exact=True).click();page.locator('.product-menu-toggle').click()
    links.last.click();assert '/urun-' in page.url
    assert not errors,errors
    # Fresh visitors see a finite opener; repeat navigation, reduced motion and no JS never block the site.
    context=browser.new_context(viewport={'width':1480,'height':900},reduced_motion='no-preference')
    page=context.new_page();page.goto(BASE+'/')
    assert page.locator('.brand-intro').is_visible()
    assert page.locator('main').evaluate('e=>e.inert')
    page.wait_for_timeout(700);page.screenshot(path='/workspace/leddisplay-marka-acilis.png')
    page.wait_for_selector('.brand-intro',state='detached',timeout=9000)
    assert not page.locator('main').evaluate('e=>e.inert')
    assert page.evaluate('getComputedStyle(document.documentElement).overflow')!='hidden'
    page.reload();assert page.locator('.brand-intro').count()==0
    page.evaluate('sessionStorage.clear()');page.reload();page.get_by_role('button',name='Açılışı geç').click()
    page.wait_for_selector('.brand-intro',state='detached');assert not page.locator('main').evaluate('e=>e.inert')
    context=browser.new_context(viewport={'width':390,'height':844})
    page=context.new_page();page.goto(BASE+'/');assert page.locator('.brand-intro').is_visible()
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    page.keyboard.press('Escape');page.wait_for_selector('.brand-intro',state='detached')
    page=browser.new_page(java_script_enabled=False);page.goto(BASE+'/');assert page.locator('.brand-intro').count()==0;assert page.locator('h1').is_visible()
    assert page.goto(BASE+'/nonexistent-page').status==404
    browser.close()
print('48 clean routes and legacy 301s with queries; six image-rich pages at six widths; all 31 hover/focus previews; mobile navigation; finite/skippable/session-aware/reduced-motion/no-JS brand opener passed.')
