"""Exercise real PHP mail handling against a local capture transport; never send real email."""
import contextlib
import http.cookiejar
import json
from pathlib import Path
import shutil
import socket
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
import uuid
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
PHP=shutil.which('php') or str(ROOT.parent/'.tools/leddisplay-php/php')
if not Path(PHP).exists():
    raise SystemExit('PHP 8.1+ is required for npm run test:contact.')

@contextlib.contextmanager
def server(frontend=False):
    with tempfile.TemporaryDirectory(prefix='leddisplay-contact-test-') as tmp:
        folder=Path(tmp);web=folder/'web';runtime=folder/'runtime';runtime.mkdir();web.mkdir()
        (web/'api').mkdir();(web/'data').mkdir()
        shutil.copy2(ROOT/'api/contact.php',web/'api/contact.php')
        shutil.copy2(ROOT/'data/products.json',web/'data/products.json')
        if frontend:
            shutil.copy2(ROOT/'iletisim.html',web/'iletisim.html');(web/'assets').mkdir()
            for name in ['style.css','app.js','favicon.svg']:
                shutil.copy2(ROOT/'assets'/name,web/'assets'/name)
        outbox=folder/'outbox';outbox.mkdir();failure=folder/'reject-mail'
        capture=folder/'sendmail.py'
        capture.write_text('import sys,uuid\nfrom pathlib import Path\n'+
            f'failure=Path({str(failure)!r})\n'+
            'if failure.exists():sys.exit(1)\n'+
            f'outbox=Path({str(outbox)!r})\n'+
            '(outbox/(uuid.uuid4().hex+".eml")).write_bytes(sys.stdin.buffer.read())\n')
        with socket.socket() as sock:
            sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
        url=f'http://127.0.0.1:{port}'
        log=(folder/'server.log').open('w+')
        process=subprocess.Popen([PHP,'-n','-d',f'sendmail_path=python3 {capture}','-d',f'session.save_path={runtime}',
            '-d',f'sys_temp_dir={runtime}','-S',f'127.0.0.1:{port}','-t',str(web)],stdout=log,stderr=log)
        try:
            for attempt in range(100):
                if process.poll() is not None:raise AssertionError('PHP test server failed to start')
                try:
                    with socket.create_connection(('127.0.0.1',port),timeout=.1):break
                except OSError:time.sleep(.05)
            yield url,outbox,failure
        finally:
            process.terminate();process.wait(timeout=10);log.close()

def client():return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
def request(opener,url,body=None,method=None,headers=None):
    data=None if body is None else json.dumps(body,ensure_ascii=False).encode()
    req=urllib.request.Request(url+'/api/contact.php',data=data,method=method,headers={'Content-Type':'application/json',**(headers or {})})
    try:
        response=opener.open(req)
    except urllib.error.HTTPError as error:response=error
    with response:return response.status,json.loads(response.read())

title1='GOB P1.86 İç Mekân LED Modül';title2='H1.25 İç Mekân LED Modül'
with server() as (url,outbox,failure):
    opener=client();status,body=request(opener,url);assert status==200
    payload=dict(csrf=body['csrf'],requestId=str(uuid.uuid4()),name='Test Kullanıcı',company='Test Firma',email='visitor@example.com',
        phone='0500 000 00 00',solution='Ürün seçimi / genel bilgi',message='İstanbul iç mekân projesi için iki ürün değerlendiriyoruz.',products=[title1,title2],website='')
    assert request(opener,url,method='PUT')[0]==405
    assert request(opener,url,payload|{'csrf':'invalid'})[0]==403
    assert request(opener,url,payload,headers={'Origin':'https://unrelated.example'})[0]==403
    assert request(opener,url,payload|{'email':'bad\r\nBcc: other@example.com'})[0]==422
    assert request(opener,url,payload|{'products':['Unlisted product']})[0]==422
    assert request(opener,url,payload|{'products':'not-an-array'})[0]==422
    assert request(opener,url,payload|{'website':'bot.example'})[0]==422
    assert request(opener,url,payload|{'message':'x'*40000})[0]==413
    assert not list(outbox.iterdir())
    status,result=request(opener,url,payload);assert status==200 and result['ok'] and result['reference'].startswith('LD-')
    messages=list(outbox.glob('*.eml'));assert len(messages)==1
    content=messages[0].read_text()
    assert 'To: info@leddisplay.com.tr' in content and 'Reply-To: visitor@example.com' in content
    assert title1 in content and title2 in content and 'İstanbul' in content and 'Test Firma' in content
    assert request(opener,url,payload)==(200,result)
    assert len(list(outbox.iterdir()))==1,'A retry must not send duplicate mail'
    assert request(opener,url,payload|{'message':'Farklı bir açıklama ile aynı gönderim kimliği.'})[0]==409
    failure.touch();retry=payload|{'requestId':str(uuid.uuid4())}
    assert request(opener,url,retry)[0]==503
    assert len(list(outbox.iterdir()))==1
    failure.unlink();assert request(opener,url,retry)[0]==200
    for _ in range(2):assert request(opener,url,payload|{'requestId':str(uuid.uuid4())})[0]==200
    assert request(opener,url,payload|{'requestId':str(uuid.uuid4())})[0]==429
    another=client();_,token=request(another,url)
    assert request(another,url,payload|{'csrf':token['csrf'],'requestId':str(uuid.uuid4())})[0]==429
    print('PHP transport: validation, CSRF/origin, two-product message, fixed recipient/Reply-To, idempotency, mail failure/retry and cross-session rate limit passed.')

with server(frontend=True) as (url,outbox,failure):
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        page=browser.new_page(viewport={'width':1440,'height':1000},reduced_motion='reduce')
        page.goto(url+'/iletisim.html',wait_until='domcontentloaded')
        page.locator('[name=name]').fill('Tarayıcı Testi');page.locator('[name=email]').fill('browser@example.com')
        page.locator('[name=message]').fill('Çoklu ürün seçimi ile doğrudan gönderim testi.')
        page.locator(f'input[name=products][value="{title1}"]').check();page.locator(f'input[name=products][value="{title2}"]').check()
        failure.touch();page.get_by_role('button',name='Talebi gönder',exact=True).click()
        page.wait_for_function("document.querySelector('#form-status').classList.contains('form-status-error')")
        assert page.locator('#project-form').is_visible() and not page.locator('#contact-success').is_visible()
        assert page.locator('[name=name]').input_value()=='Tarayıcı Testi'
        assert page.locator('input[name=products]:checked').count()==2
        assert not list(outbox.iterdir())
        failure.unlink();page.get_by_role('button',name='Talebi gönder',exact=True).click()
        page.wait_for_function("!document.querySelector('#contact-success').hidden")
        assert not page.locator('#project-form').is_visible()
        assert page.url==url+'/iletisim.html'
        assert len(list(outbox.iterdir()))==1
        captured=next(outbox.iterdir()).read_text();assert title1 in captured and title2 in captured
        assert page.locator('#contact-reference').inner_text() in captured
        for width in [1440,768,390,360]:
            page.set_viewport_size({'width':width,'height':900});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.set_viewport_size({'width':1440,'height':1000})
        page.locator('#contact-success').screenshot(path='/workspace/leddisplay-form-basari-onizleme.png')
        page.get_by_role('button',name='Yeni bir talep oluştur').click()
        assert page.locator('#project-form').is_visible() and page.locator('[name=name]').input_value()==''
        assert page.locator('input[name=products]:checked').count()==0
        browser.close()
        print('Real PHP + Chromium: failed mail retains inputs; retry sends both products, stays on-page, shows matching reference, adapts to mobile and resets for a new request.')
