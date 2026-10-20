"""Exercise hero media, responsive framing and actual motion controls."""
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    context=browser.new_context(viewport={'width':1440,'height':1000})
    context.add_init_script("sessionStorage.setItem('leddisplay-intro-v3','1')")
    page=context.new_page();errors=[]
    page.on('pageerror',lambda error:errors.append(str(error)))
    for width,height in [(1920,1080),(1440,1000),(1024,768),(768,1024),(390,844)]:
        page.set_viewport_size({'width':width,'height':height})
        page.goto('http://127.0.0.1:3000/')
        page.locator('.corporate-hero-visual>img').evaluate('(img)=>img.decode()')
        page.wait_for_timeout(150)
        assert page.locator('[data-sphere-hero]').count()==1
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),width
        visual=page.locator('.corporate-hero-visual').bounding_box()
        glow=page.locator('.hero-led-glow').bounding_box()
        assert visual['x']==0 and visual['width']==width,(width,visual)
        assert glow['y']>=visual['y']-2 and glow['y']+glow['height']<=visual['y']+visual['height']+2,(width,'sphere cropped vertically')
        assert page.locator('.corporate-hero .hero-project-reference').count()==0,'Visualization must not be labelled as the Ankara installation'
        assert '/assets/hero/' in page.locator('meta[property="og:image"]').get_attribute('content')
        page.screenshot(path=f'/workspace/leddisplay-sphere-{width}.png')
    page.set_viewport_size({'width':1440,'height':1000})
    page.goto('http://127.0.0.1:3000/')
    button=page.locator('.sphere-motion-toggle');glow=page.locator('.hero-led-glow')
    page.wait_for_function('document.querySelector("[data-sphere-hero]").classList.contains("sphere-motion-ready")')
    button.click()
    assert button.get_attribute('aria-pressed')=='true'
    first=glow.evaluate('(el)=>getComputedStyle(el,"::before").transform')
    page.wait_for_timeout(150)
    assert glow.evaluate('(el)=>getComputedStyle(el,"::before").transform')==first,'Paused light moved'
    button.click();assert button.get_attribute('aria-pressed')=='false'
    page.wait_for_timeout(200)
    assert glow.evaluate('(el)=>getComputedStyle(el,"::before").transform')!=first,'Light did not resume'
    page.emulate_media(reduced_motion='reduce');page.wait_for_timeout(100)
    assert button.get_attribute('aria-pressed')=='true'
    assert 'sphere-is-still' in page.locator('[data-sphere-hero]').get_attribute('class')
    page.emulate_media(reduced_motion='no-preference')
    page.locator('#uygulamalar').scroll_into_view_if_needed();page.wait_for_timeout(150)
    assert 'sphere-is-still' in page.locator('[data-sphere-hero]').get_attribute('class'),'Offscreen light kept running'
    page.goto('http://127.0.0.1:3000/projeler')
    assert page.locator('script[src*="sphere-hero"],link[href*="sphere-hero"]').count()==0
    assert not errors,errors
    print('Sphere hero: five viewports, framing, pause/resume, reduced motion and offscreen suspension passed.')
    browser.close()
