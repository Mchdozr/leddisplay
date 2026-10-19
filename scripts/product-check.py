"""Regression checks for dropdown pointer travel and stable product galleries."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
products=json.loads((root/'data/products.json').read_text())
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1440,'height':1000},reduced_motion='reduce')
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto('http://localhost:3000/',wait_until='domcontentloaded')
    trigger=page.locator('.nav-product-group>a').bounding_box()
    page.mouse.move(trigger['x']+trigger['width']/2,trigger['y']+trigger['height']/2)
    page.wait_for_function("document.querySelector('.nav-product-group').classList.contains('is-open')")
    link=page.get_by_role('link',name='GOB kaplamalı modüller',exact=True)
    box=link.bounding_box()
    page.mouse.move(box['x']+box['width']/2,box['y']+box['height']/2,steps=18)
    # Stay beyond the close-delay to catch a submenu disappearing under the pointer.
    page.wait_for_timeout(350)
    assert page.locator('#product-megamenu').is_visible()
    link.click()
    assert page.locator('#series-filter').input_value()=='gob'
    changed=0
    for width in [1440,390]:
        page.set_viewport_size({'width':width,'height':1000})
        for product in products:
            page.goto('http://localhost:3000/urun-'+product['slug']+'.html',wait_until='domcontentloaded')
            assert page.locator('.product-info').is_visible()
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),product['slug']
            if not product['image']:
                assert page.locator('.gallery-placeholder').is_visible()
                continue
            stage=page.locator('.gallery-stage')
            assert stage.bounding_box()['height']<=400
            assert page.locator('#product-main-image').evaluate('(e)=>getComputedStyle(e).objectFit')=='contain'
            info_before=page.locator('.product-info').bounding_box()
            info_before_y=info_before['y']+page.evaluate('scrollY')
            stage_before=stage.bounding_box()
            second=page.locator('[data-gallery-src]').nth(1)
            if product['backImage']:
                second.click()
                info_after=page.locator('.product-info').bounding_box()
                assert abs(info_before_y-(info_after['y']+page.evaluate('scrollY')))<1,product['slug']+' info moved'
                assert abs(stage_before['height']-stage.bounding_box()['height'])<1
                assert page.locator('#product-main-image').get_attribute('src')==product['backImage']
                assert second.get_attribute('aria-pressed')=='true'
                assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
                changed+=1
            stage.click()
            dialog=page.locator('.product-image-dialog')
            assert dialog.is_visible()
            bounds=dialog.bounding_box()
            assert bounds['height']<=page.viewport_size['height']-35
            assert bounds['width']<=width
            if product['backImage']:assert dialog.locator('img').get_attribute('src').endswith(product['backImage'])
            page.keyboard.press('Escape')
            assert not dialog.is_visible()
            page.wait_for_function('!document.documentElement.classList.contains("product-image-open")')
    page.set_viewport_size({'width':1440,'height':1000})
    page.goto('http://localhost:3000/urun-grand-air-ic-mekan.html')
    page.get_by_role('button',name='500 × 1000 mm kabin seçeneği',exact=True).click()
    page.locator('#product-main-image').evaluate('(image)=>image.decode()')
    page.locator('.product-detail').screenshot(path='/workspace/leddisplay-urun-galeri-onizleme.png')
    assert not errors,errors
    browser.close()
    print(f'All {len(products)} product pages at desktop/mobile widths passed; {changed} secondary-view changes kept layout stable. Dropdown pointer travel and image viewer passed.')
