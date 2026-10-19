"""Check scroll entry continuity, stable geometry and reduced-motion cleanup."""
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    for width in [1440,390]:
        for path,selector in [('/','.series-card'),('/urunler.html','.product-card:nth-child(18)')]:
            page=browser.new_page(viewport={'width':width,'height':900},reduced_motion='no-preference')
            page.goto('http://localhost:3000'+path,wait_until='networkidle')
            target=page.locator(selector).first
            assert target.get_attribute('data-entry-pending') is not None
            samples=target.evaluate('''async element=>{
                const docY=element.getBoundingClientRect().top+scrollY;
                window.scrollTo({top:docY-innerHeight+35,behavior:'instant'});
                const frames=[];
                for(let i=0;i<85;i++){
                    await new Promise(requestAnimationFrame);
                    const style=getComputedStyle(element);
                    frames.push({y:parseFloat(style.translate.split(' ')[1])||0,opacity:style.opacity,transform:style.transform});
                }
                return frames;
            }''')
            assert all(sample['opacity']=='1' for sample in samples)
            assert all(b['y']<=a['y']+.15 for a,b in zip(samples,samples[1:])), 'Entry jumped backward'
            assert samples[-1]['y']==0, 'Entry did not settle'
            assert target.evaluate('(e)=>e.style.willChange')=='', 'Temporary layer retained'
            assert target.evaluate('(e)=>e.getAnimations().length')==0
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            # Preference changes clear every pre-positioned card, not just active effects.
            page.emulate_media(reduced_motion='reduce')
            page.wait_for_function("!document.querySelector('[data-entry-pending]')")
            page.close()
    browser.close()
    print('Desktop/mobile homepage and catalog: full opacity, monotonic upward movement, no end snap, layer cleanup and reduced-motion cleanup passed.')
