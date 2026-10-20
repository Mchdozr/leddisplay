"""Real-project navigation and media tests. Contact submissions use a mock, never email."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
projects=json.loads((ROOT/'data/projects.json').read_text())
BASE='http://127.0.0.1:3000'
public=[f.stem for f in ROOT.glob('*.html') if not f.stem.startswith('urun-') and f.stem not in ['urunler','404']]
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    context=browser.new_context(viewport={'width':1440,'height':1000},reduced_motion='reduce')
    context.add_init_script("sessionStorage.setItem('leddisplay-intro-v3','1')")
    context.route('https://fonts.googleapis.com/**',lambda route:route.abort())
    context.route('https://fonts.gstatic.com/**',lambda route:route.abort())
    page=context.new_page();errors=[];videos=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.on('request',lambda r:videos.append(r.url) if '/assets/projects/' in r.url and '.mp4' in r.url else None)
    for width in [1440,1024,768,390]:
        page.set_viewport_size({'width':width,'height':900 if width>768 else 844})
        for slug in public:
            response=page.goto(BASE+('/' if slug=='index' else '/'+slug),wait_until='domcontentloaded')
            assert response.status==200,(slug,response.status)
            assert page.locator('h1').count()==1,slug
            assert page.locator('main').inner_text().strip(),slug
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),(slug,width,'overflow')
            assert page.locator('a[href^="/urunler"],a[href^="/urun-"],img[src^="/assets/products/"]').count()==0,slug
    assert not videos,('Project videos loaded before play',videos)
    for route in ['/urunler','/urunler.html','/urun-grand-air-ic-mekan','/kiralik-led-ekran','/assets/spec/gob-1-86-ic-mekan.pdf','/assets/products/gob-1-86-ic-mekan-front.jpg','/assets/catalog-experience.json','/data/projects.json']:
        response=context.request.get(BASE+route);assert response.status==404,(route,response.status)
    page.set_viewport_size({'width':1440,'height':1000})
    page.goto(BASE+'/projeler');assert page.locator('.reference-card').count()==len(projects)
    page.screenshot(path='/workspace/leddisplay-projeler-desktop.png',full_page=True)
    page.goto(BASE+'/proje-ankara-dis-isleri')
    assert page.locator('.project-facts').inner_text().find('7 Ocak 2026')>=0
    assert 'Yapılış tarihi' in page.locator('.project-facts').inner_text()
    assert 'Fatura' not in page.locator('.project-facts').inner_text()
    assert page.locator('video').count()==1
    page.locator('[data-project-photo]').first.click()
    assert page.locator('.project-lightbox').is_visible()
    before=page.locator('.project-lightbox>img').get_attribute('src')
    page.keyboard.press('ArrowRight')
    assert page.locator('.project-lightbox>img').get_attribute('src')!=before
    page.keyboard.press('Escape');assert not page.locator('.project-lightbox').is_visible()
    assert page.locator('[data-project-photo]').first.evaluate('(el)=>el===document.activeElement')
    page.screenshot(path='/workspace/leddisplay-ankara-proje.png',full_page=True)
    page.goto(BASE+'/proje-izmir-homend')
    assert page.locator('video').count()==2
    assert page.locator('.project-document-note').inner_text().find('kurulum aşamasına')>=0
    page.locator('video').first.evaluate('(v)=>v.play()')
    page.wait_for_timeout(700)
    assert videos,'Video did not load after play'
    page.locator('video').first.evaluate('(v)=>v.pause()')
    for project in projects:
        page.goto(BASE+'/proje-'+project['slug'])
        assert page.locator('video').count()==len(project['videos'])
        assert page.locator('[data-project-photo]').count()==len(project['gallery'])
        assert page.locator('.project-facts').inner_text().find('Fatura')==-1
        assert len({v['src'] for v in project['videos']})==len(project['videos'])
        if not project.get('cover'):
            assert page.locator('.project-record-banner').is_visible()
            assert page.locator('.project-banner,.project-gallery-section,.project-video-section').count()==0
            assert page.locator('meta[property="og:image"]').get_attribute('content').endswith('/assets/leddisplay-logo-navy.png')
            page.locator('a[href="#uygulama-kapsami"]').click()
            assert page.locator('#uygulama-kapsami').is_visible()
    page.goto(BASE+'/proje-zorlu-center-gant')
    assert 'Ek uygulama tarihi' in page.locator('.project-facts').inner_text()
    assert '15 Mayıs 2026' in page.locator('.project-facts').inner_text()
    assert 'Ana kolon ekranının kesin yapılış günü' in page.locator('.project-document-note').inner_text()
    page.set_viewport_size({'width':390,'height':844})
    page.goto(BASE+'/projeler');page.screenshot(path='/workspace/leddisplay-projeler-mobile.png',full_page=True)
    page.get_by_role('button',name='Menüyü aç',exact=True).click()
    assert page.locator('#navigation a[href="/projeler"]').is_visible()
    assert page.locator('#navigation a[href="/projeler"]').get_attribute('aria-current')=='page'
    page.goto(BASE+'/proje-izmir-homend');page.screenshot(path='/workspace/leddisplay-homend-mobile.png',full_page=True)
    # The working form sends an empty product list after removing the catalog picker.
    requests=[]
    def contact(route):
        if route.request.method=='GET':route.fulfill(json={'ok':True,'csrf':'local-project-test-token'})
        else:
            requests.append(route.request.post_data_json)
            route.fulfill(json={'ok':True,'reference':'LD-261020-1234ABCD'})
    page.route('**/api/contact.php',contact)
    page.goto(BASE+'/iletisim')
    page.locator('[name=name]').fill('Proje Testi')
    page.locator('[name=email]').fill('test@example.com')
    page.locator('[name=message]').fill('Yeni mağaza projemiz için anahtar teslim LED ekran uygulaması talep ediyoruz.')
    assert page.locator('.product-picker').count()==0
    with page.expect_download() as downloaded:page.locator('button[name=action][value=download]').click()
    assert 'anahtar teslim' in Path(downloaded.value.path()).read_text(encoding='utf-8-sig')
    page.get_by_role('button',name='Talebi gönder',exact=True).click()
    page.locator('#contact-success').wait_for(state='visible')
    assert requests[0]['products']==[]
    page.get_by_role('button',name='Yeni bir talep oluştur').click()
    assert page.locator('#project-form').is_visible()
    assert not errors,errors
    # Desktop project section pins while all featured projects move horizontally.
    page.emulate_media(reduced_motion='no-preference');page.set_viewport_size({'width':1440,'height':1000})
    page.goto(BASE+'/');page.wait_for_timeout(400)
    page.screenshot(path='/workspace/leddisplay-gercek-projeler-hero.png')
    assert page.locator('.showcase-pinned').count()==1
    assert page.locator('.showcase-card').count()==sum(bool(project.get('featured')) for project in projects)
    geometry=page.locator('.showcase-section').evaluate('(el)=>({start:el.getBoundingClientRect().top+scrollY-document.querySelector(".header").offsetHeight,height:el.offsetHeight,stage:el.querySelector(".showcase-stage").offsetHeight})')
    tops=[]
    for progress in [.2,.7]:
        y=geometry['start']+(geometry['height']-geometry['stage'])*progress
        page.evaluate('(y)=>scrollTo({top:y,behavior:"instant"})',y);page.wait_for_timeout(100)
        tops.append(page.locator('.showcase-stage').bounding_box()['y'])
    assert abs(tops[0]-tops[1])<2,('Pinned project section moved vertically',tops)
    page.screenshot(path='/workspace/leddisplay-gercek-projeler-scroll.png')
    # Longer shop names must not clip the project link in a laptop-height stage.
    for width in [1480,1024,901]:
        page.set_viewport_size({'width':width,'height':764})
        page.goto(BASE+'/');page.wait_for_timeout(400)
        assert page.locator('.showcase-pinned').count()==1
        geometry=page.locator('.showcase-section').evaluate('(el)=>({start:el.getBoundingClientRect().top+scrollY-document.querySelector(".header").offsetHeight,distance:el.offsetHeight-el.querySelector(".showcase-stage").offsetHeight})')
        cards=page.locator('.showcase-card')
        for index in range(cards.count()):
            page.evaluate('(y)=>scrollTo({top:y,behavior:"instant"})',geometry['start']+geometry['distance']*index/(cards.count()-1))
            page.wait_for_timeout(100)
            visible=cards.nth(index).evaluate('(el)=>{const card=el.getBoundingClientRect(),link=el.querySelector(".showcase-copy>a").getBoundingClientRect();return link.bottom<=card.bottom+1&&link.top>=card.top}')
            assert visible,('Clipped project copy',width,index)
    page.set_viewport_size({'width':1024,'height':650})
    page.wait_for_timeout(150)
    assert page.locator('.showcase-pinned').count()==0,'Short windows must let all project content flow vertically'
    assert not errors,errors
    print(f'{len(public)} public pages × 4 viewports: no overflow or catalog access; project gallery, deferred videos, pinned showcase and mocked contact flow passed.')
    browser.close()
