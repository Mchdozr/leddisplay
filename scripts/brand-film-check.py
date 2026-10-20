"""Check actual intro playback, responsive sources, escape routes and failure handling."""
import json
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
BASE = 'http://127.0.0.1:3000/'
for portrait in (False, True):
    for extension in ('mp4', 'webm'):
        file = ROOT / ('assets/video/leddisplay-brand-intro-v3' + ('-portrait' if portrait else '') + '.' + extension)
        metadata = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(file)]))
        streams = metadata['streams']
        assert len(streams) == 1 and streams[0]['codec_type'] == 'video'
        assert streams[0]['width'] == (1080 if portrait else 1920)
        assert streams[0]['height'] == (1920 if portrait else 1080)
        assert 2.6 < float(metadata['format']['duration']) < 2.8

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
    for portrait in (False, True):
        context = browser.new_context(viewport={'width': 390 if portrait else 1480, 'height': 844 if portrait else 900})
        page = context.new_page()
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.goto(BASE, wait_until='domcontentloaded')
        page.wait_for_function("document.querySelector('.intro-film')?.currentTime>.2")
        film = page.locator('.intro-film')
        assert film.evaluate('(e)=>e.muted && e.playsInline && !e.paused')
        assert ('-portrait.' in film.evaluate('(e)=>e.currentSrc')) == portrait
        assert page.locator('main').evaluate('(e)=>e.inert')
        page.wait_for_function("document.querySelector('.intro-film')?.currentTime>1.7")
        page.screenshot(path=f'/workspace/leddisplay-intro-v3-{ "mobile" if portrait else "desktop"}.png')
        page.wait_for_selector('.brand-intro', state='detached', timeout=5000)
        assert not page.locator('main').evaluate('(e)=>e.inert')
        assert page.evaluate('getComputedStyle(document.documentElement).overflow') != 'hidden'
        page.reload()
        assert page.locator('.brand-intro').count() == 0
        for action in ('button', 'Escape', 'Tab'):
            page.evaluate('sessionStorage.clear()')
            page.reload(wait_until='domcontentloaded')
            if action == 'button':
                page.get_by_role('button', name='Açılışı geç').click()
            else:
                page.keyboard.press(action)
            page.wait_for_selector('.brand-intro', state='detached')
            assert not page.locator('main').evaluate('(e)=>e.inert')
        assert not errors, errors
        context.close()

    context = browser.new_context()
    page = context.new_page()
    page.route('**/assets/video/*.webm*', lambda route: route.abort())
    page.goto(BASE, wait_until='domcontentloaded')
    page.wait_for_function("document.querySelector('.intro-film')?.currentTime>.2")
    assert page.locator('.intro-film').evaluate('(e)=>new URL(e.currentSrc).pathname.endsWith(".mp4")')
    page.get_by_role('button', name='Açılışı geç').click()
    context.close()

    context = browser.new_context(reduced_motion='reduce')
    page = context.new_page(); requests = []
    page.on('request', lambda request: requests.append(request.url))
    page.goto(BASE)
    assert page.locator('.brand-intro').count() == 0
    assert not any('brand-intro-v3' in url for url in requests)
    context.close()

    for fail in ('network', 'autoplay'):
        context = browser.new_context()
        page = context.new_page()
        if fail == 'network':
            page.route('**/assets/video/**', lambda route: route.abort())
        else:
            page.add_init_script("HTMLMediaElement.prototype.play=()=>Promise.reject(new Error('Playback blocked'))")
        page.goto(BASE, wait_until='domcontentloaded')
        page.wait_for_selector('.brand-intro', state='detached', timeout=9000)
        assert not page.locator('main').evaluate('(e)=>e.inert')
        context.close()

    page = browser.new_page(java_script_enabled=False)
    page.goto(BASE)
    assert page.locator('.brand-intro').count() == 0
    assert page.locator('h1').is_visible()
    browser.close()
print('Four silent video exports; desktop/mobile playback, session, skip, keyboard, reduced motion and failure fallbacks passed.')
