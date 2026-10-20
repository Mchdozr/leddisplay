from playwright.sync_api import sync_playwright
from pathlib import Path
import json
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 page=browser.new_page(viewport={'width':1440,'height':1000})
 page.goto('http://localhost:3000/urunler.html')
 page.locator('#series-filter').select_option('gob')
 assert page.locator('.catalog-grid .product-card:visible').count()==4
 page.locator('#environment-filter').select_option('Dış mekân')
 assert page.locator('.catalog-grid .product-card:visible').count()==0
 assert page.locator('#no-products').is_visible()
 page.get_by_role('button',name='Temizle').click()
 page.wait_for_function("document.querySelector('#product-count').textContent.startsWith('31')")
 page.locator('#product-search').fill('H1.86 İç')
 assert page.locator('.catalog-grid .product-card:visible').count()==1
 page.locator('.catalog-grid .product-card:visible').click()
 assert 'h-1-86-ic-mekan' in page.url
 assert '≥6000 Hz' in page.locator('table').inner_text()
 with page.expect_download() as d:page.get_by_role('link',name='Teknik föyü indir').click()
 assert Path(d.value.path()).read_bytes().startswith(b'%PDF-')
 page.get_by_role('link',name='Bu ürünü konuşalım').click()
 assert page.locator('input[name=products][value="H1.86 İç Mekân LED Ekran"]').is_checked()
 page.goto('http://localhost:3000/')
 for y in range(0,6500,500):
  page.evaluate('(y)=>window.scrollTo(0,y)',y)
  page.wait_for_timeout(100)
 page.evaluate('window.scrollTo(0,0)');page.wait_for_timeout(800)
 page.screenshot(path='/tmp/leddisplay-desktop.png',full_page=True)
 page.set_viewport_size({'width':390,'height':844})
 page.goto('http://localhost:3000/urunler.html')
 page.locator('#series-filter').select_option('front')
 assert page.locator('.catalog-grid .product-card:visible').count()==3
 page.screenshot(path='/tmp/leddisplay-catalog-mobile.png',full_page=True)
 # No JavaScript still exposes all content and links.
 context=browser.new_context(java_script_enabled=False)
 nojs=context.new_page();nojs.goto('http://localhost:3000/')
 assert nojs.locator('h1').is_visible()
 print(json.dumps({'catalog_filters':'passed','empty_state':'passed','reset':'passed','model_search':'passed','pdf_download':'passed','product_to_contact':'passed','mobile_catalog':'passed'}))
 browser.close()
