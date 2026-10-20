"""Validate product navigation, compact headers, catalog categories and multi-product email drafts."""
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1440,'height':1000},reduced_motion='reduce')
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto('http://localhost:3000/',wait_until='networkidle')
    assert page.locator('#navigation').get_by_role('link',name='Anasayfa',exact=True).is_visible()
    page.locator('.nav-product-group').hover()
    assert page.locator('#product-megamenu').is_visible()
    assert page.locator('.mega-column').count()==3
    page.keyboard.press('Escape')
    assert not page.locator('#product-megamenu').is_visible()
    page.locator('.product-menu-toggle').click()
    page.locator('.mega-product[href="/urun-gob-1-86-ic-mekan"]').click()
    assert page.url.endswith('/urun-gob-1-86-ic-mekan')
    page.goto('http://localhost:3000/urunler?seri=gob')
    assert page.locator('#series-filter').input_value()=='gob'
    assert page.locator('.catalog-grid .product-card:visible').count()==4
    page.locator('[data-catalog-series="rental"]').click()
    assert page.locator('.catalog-grid .product-card:visible').count()==2
    assert page.locator('[data-catalog-series="rental"]').get_attribute('aria-pressed')=='true'
    page.goto('http://localhost:3000/urunler.html?seri=h&ortam=dis')
    assert page.locator('.catalog-grid .product-card:visible').count()==4
    for width in [1440,1024,768,390,360]:
        page.set_viewport_size({'width':width,'height':900})
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),f'catalog overflow {width}'
    page.set_viewport_size({'width':390,'height':844})
    page.get_by_role('button',name='Menüyü aç').click()
    page.locator('.product-menu-toggle').click()
    assert page.locator('#product-megamenu').is_visible()
    page.locator('.mega-column').first.get_by_role('link',name='Çözümü keşfedin').click()
    assert page.url.endswith('/ic-mekan-led-ekran')
    page.goto('http://localhost:3000/urunler?ortam=ic')
    assert page.locator('#environment-filter').input_value()=='İç mekân'
    page.goto('http://localhost:3000/iletisim.html?urun=GOB%20P1.86%20İç%20Mekân%20LED%20Modül')
    assert page.locator('.page-hero').bounding_box()['height']<260
    first=page.locator('input[name=products][value="GOB P1.86 İç Mekân LED Ekran"]')
    assert first.is_checked()
    second=page.locator('input[name=products][value="H1.25 İç Mekân LED Ekran"]')
    second.check()
    assert '2 ürün' in page.locator('#selected-products-count').inner_text()
    page.locator('#picker-search').fill('Grand Air')
    assert page.locator('.product-option:visible').count()==2
    assert first.is_checked() and second.is_checked()
    page.locator('[name=name]').fill('Test Kullanıcı')
    page.locator('[name=email]').fill('test@example.com')
    page.locator('[name=message]').fill('İki ürün için İstanbul projesine teklif istiyorum.')
    with page.expect_download() as download:
        page.get_by_role('button',name='Proje özetini indir').click()
    text=Path(download.value.path()).read_text(encoding='utf-8-sig')
    assert 'GOB P1.86 İç Mekân LED Ekran' in text and 'H1.25 İç Mekân LED Ekran' in text
    for width in [1440,768,390,360]:
        page.set_viewport_size({'width':width,'height':900})
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),f'contact overflow {width}'
    page.screenshot(path='/workspace/leddisplay-iletisim-onizleme.png',full_page=True)
    page.goto('http://localhost:3000/')
    assert page.locator('.knowledge-photo').count()==3
    assert page.locator('.knowledge-photo').evaluate_all('cards=>cards.every(e=>getComputedStyle(e).backgroundImage!=="none")')
    assert not errors,errors
    # Restore upward-only entry motion, without any opacity keyframes.
    animated=browser.new_page(viewport={'width':1440,'height':1000},reduced_motion='no-preference')
    animated.add_init_script('''window.entryFrames=[];const original=Element.prototype.animate;Element.prototype.animate=function(frames,options){window.entryFrames.push(frames);return original.call(this,frames,options)}''')
    animated.add_init_script("sessionStorage.setItem('leddisplay-intro-v3','1')")
    animated.goto('http://localhost:3000/')
    animated.locator('.series-card').first.scroll_into_view_if_needed()
    animated.wait_for_function("document.querySelector('.series-card').classList.contains('motion-seen')")
    assert animated.evaluate("entryFrames.some(frames=>frames[0].translate && frames[0].translate.endsWith('18px'))")
    assert animated.evaluate("entryFrames.every(frames=>frames.every(frame=>!('opacity' in frame)))")
    assert animated.locator('.series-card').first.evaluate('(e)=>getComputedStyle(e).opacity')=='1'
    browser.close()
    print('Navigation, category URLs, mobile menu, compact banner, multi-product selection/download, guide images and opacity-free entry motion passed.')
