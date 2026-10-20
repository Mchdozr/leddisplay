"""Check project discovery, shareable filters and the visual navigation with real layouts."""
import json
from pathlib import Path
from urllib.parse import parse_qs, urlparse
from playwright.sync_api import sync_playwright, expect

ROOT=Path(__file__).resolve().parents[1]
PROJECTS=json.loads((ROOT/'data/projects.json').read_text())
BASE='http://127.0.0.1:3000'

with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    context=browser.new_context(viewport={'width':1440,'height':1000})
    context.add_init_script("sessionStorage.setItem('leddisplay-intro-v3','1')")
    page=context.new_page()
    errors=[]
    page.on('pageerror',lambda error:errors.append(str(error)))

    page.goto(BASE+'/projeler',wait_until='networkidle')
    tools=page.locator('.project-archive-tools')
    expect(tools).to_be_visible()
    buttons=page.locator('[data-project-filter]')
    cards=page.locator('.reference-card')
    assert cards.count()==len(PROJECTS)
    assert sum(int(text) for text in buttons.locator('span').all_text_contents()[1:])==len(PROJECTS)
    for button in buttons.all():
        button.click()
        expected=int(button.locator('span').inner_text())
        assert page.locator('.reference-card:not([hidden])').count()==expected
        expect(button).to_have_attribute('aria-pressed','true')
        assert page.locator('[data-project-filter][aria-pressed=true]').count()==1
        assert page.locator('[data-project-count]').inner_text().startswith(str(expected)+' proje')
        if button.get_attribute('data-project-filter')!='all':
            assert parse_qs(urlparse(page.url).query)['sektor']==[button.get_attribute('data-project-filter')]

    page.locator('[data-project-filter=all]').click()
    search=page.locator('#project-search')
    for term,expected_slug in [('İSTİNYEPARK','istinyepark-homend'),('colins','ankara-colins'),('ITU','itu-maslak')]:
        search.fill(term)
        assert page.locator('.reference-card:not([hidden])').count()==1,term
        assert expected_slug in page.locator('.reference-card:not([hidden]) h2>a').get_attribute('href')
    search.fill('Homend')
    assert page.locator('.reference-card:not([hidden])').count()==2
    page.locator('[data-project-filter=retail]').click()
    shared=page.url
    page.reload(wait_until='networkidle')
    expect(search).to_have_value('Homend')
    expect(page.locator('[data-project-filter=retail]')).to_have_attribute('aria-pressed','true')
    assert page.locator('.reference-card:not([hidden])').count()==2
    assert page.url==shared
    page.locator('[data-project-filter=education]').click()
    expect(page.locator('.project-no-results')).to_be_visible()
    assert page.locator('.reference-card:not([hidden])').count()==0
    page.locator('[data-project-reset]').click()
    assert page.locator('.reference-card:not([hidden])').count()==len(PROJECTS)
    expect(search).to_be_focused()
    assert not urlparse(page.url).query
    page.goto(BASE+'/projeler?sektor=mall')
    assert page.locator('.reference-card:not([hidden])').count()==2
    page.goto(BASE+'/projeler?sektor=unknown')
    assert page.locator('.reference-card:not([hidden])').count()==len(PROJECTS)

    for width,height in [(1440,1000),(1024,764),(901,764),(768,1024),(390,844),(320,740)]:
        page.set_viewport_size({'width':width,'height':height})
        page.goto(BASE+'/projeler',wait_until='networkidle')
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),('archive overflow',width)
        if width==390:
            page.evaluate('scrollTo({top:document.querySelector(".project-archive-tools").getBoundingClientRect().top+scrollY-100,behavior:"instant"})')
            page.screenshot(path='/workspace/leddisplay-project-search-mobile.png')
        page.goto(BASE+'/',wait_until='networkidle')
        page.evaluate('document.documentElement.style.scrollBehavior="auto"')
        pinned=width>=901 and height>=740
        assert page.locator('.showcase-pinned').count()==int(pinned)
        if pinned:
            geometry=page.locator('.showcase-section').evaluate('''el=>({
                start:el.getBoundingClientRect().top+scrollY-document.querySelector('.header').offsetHeight,
                distance:el.offsetHeight-el.querySelector('.showcase-stage').offsetHeight,
                top:document.querySelector('.header').offsetHeight
            })''')
            for index in range(4):
                page.evaluate('y=>scrollTo({top:y,behavior:"instant"})',geometry['start']+geometry['distance']*index/3)
                page.wait_for_timeout(150)
                expect(page.locator(f'[data-project-step="{index}"]')).to_have_attribute('aria-current','step')
                stage=page.locator('.showcase-stage').bounding_box()
                assert abs(stage['y']-geometry['top'])<2,('vertical pin movement',width,index)
                visible=page.locator('.showcase-card').nth(index).evaluate('''el=>{
                    const card=el.getBoundingClientRect(),copy=el.querySelector('.showcase-copy').getBoundingClientRect(),
                    first=el.querySelector('.showcase-copy-heading').getBoundingClientRect(),
                    last=el.querySelector('.showcase-copy>a').getBoundingClientRect();
                    return first.top>=card.top&&last.bottom<=card.bottom+1&&last.right<=copy.right+1;
                }''')
                assert visible,('clipped project content',width,index)
            page.locator('[data-project-step="1"]').click()
            page.wait_for_timeout(1400)
            expect(page.locator('[data-project-step="1"]')).to_have_attribute('aria-current','step')
            if width==1440:
                page.screenshot(path='/workspace/leddisplay-project-showcase-desktop.png')
        else:
            assert page.locator('.showcase-navigation').is_hidden()
            for card in page.locator('.showcase-card').all():
                assert card.bounding_box()['height']>450
            if width==390:
                page.evaluate('scrollTo({top:document.querySelector(".showcase-section").getBoundingClientRect().top+scrollY-85,behavior:"instant"})')
                page.wait_for_timeout(800)
                page.screenshot(path='/workspace/leddisplay-project-showcase-mobile.png')
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),('home overflow',width)
        page.goto(BASE+'/proje-ankara-dis-isleri')
        assert page.locator('.related-project-card').count()==3
        assert all('/proje-ankara-dis-isleri' not in link.get_attribute('href') for link in page.locator('.related-project-card').all())
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),('related overflow',width)

    page.set_viewport_size({'width':1440,'height':1000})
    page.emulate_media(reduced_motion='reduce')
    page.goto(BASE+'/')
    assert page.locator('.showcase-pinned').count()==0
    assert page.locator('.showcase-grid').evaluate('el=>!el.style.transform')
    no_js=browser.new_context(java_script_enabled=False,viewport={'width':390,'height':844})
    static=no_js.new_page()
    static.goto(BASE+'/projeler')
    assert static.locator('.reference-card:not([hidden])').count()==len(PROJECTS)
    assert static.locator('.project-archive-tools').is_hidden()
    static.goto(BASE+'/')
    assert static.locator('.showcase-card').count()==4
    assert static.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
    assert not errors,errors
    browser.close()
    print('Project filtering, Turkish search, shared state, empty results, photo navigation, pinned layouts and no-JS/reduced-motion fallbacks passed.')
