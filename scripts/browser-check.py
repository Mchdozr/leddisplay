from playwright.sync_api import sync_playwright
from pathlib import Path
import json
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 page=browser.new_page(viewport={'width':1440,'height':1000},device_scale_factor=1)
 errors=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 results=[]
 for file in sorted(Path(__file__).resolve().parents[1].glob('*.html')):
  response=page.goto('http://127.0.0.1:3000/'+file.name,wait_until='domcontentloaded')
  assert response.status==200
  assert page.locator('h1').count()==1
  assert page.locator('main').inner_text().strip()
  results.append(file.name)
 page.goto('http://127.0.0.1:3000/',wait_until='networkidle')
 page.screenshot(path='/tmp/leddisplay-desktop.png',full_page=True)
 assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'), 'desktop overflow'
 page.goto('http://127.0.0.1:3000/iletisim.html')
 page.locator('[name=name]').fill('Test Kullanıcı')
 page.locator('[name=email]').fill('test@example.com')
 page.locator('[name=message]').fill('İstanbul için 4 x 3 metre iç mekân ekran projesi.')
 with page.expect_download() as dl:
  page.get_by_role('button',name='Proje özetini indir').click()
 download=dl.value
 assert 'İstanbul' in Path(download.path()).read_text(encoding='utf-8-sig')
 assert 'gönderilmedi' in page.locator('#form-status').inner_text()
 for width in [390,768]:
  page.set_viewport_size({'width':width,'height':844})
  for file in sorted(Path(__file__).resolve().parents[1].glob('*.html')):
   page.goto('http://127.0.0.1:3000/'+file.name,wait_until='domcontentloaded')
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),file.name+' overflow '+str(width)
 page.set_viewport_size({'width':390,'height':844})
 page.goto('http://127.0.0.1:3000/')
 page.get_by_role('button',name='Menüyü aç').click()
 assert page.locator('#navigation').is_visible()
 page.keyboard.press('Escape')
 assert not page.locator('#navigation').is_visible()
 page.screenshot(path='/tmp/leddisplay-mobile.png',full_page=True)
 assert not errors,errors
 print(json.dumps({'pages':len(results),'desktop':'passed','mobile_widths':[390,768],'navigation':'passed','download_form':'passed','javascript_errors':errors}))
 browser.close()
