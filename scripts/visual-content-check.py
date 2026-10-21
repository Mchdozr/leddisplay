"""Compare a visual-only build with an explicit committed content baseline."""
import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REFERENCE=sys.argv[1] if len(sys.argv)>1 else 'HEAD'

class Content(HTMLParser):
    def __init__(self,html):
        super().__init__(convert_charrefs=True)
        self.skip=0;self.text=[];self.links=[];self.fields=[];self.media=[]
        self.feed(html)
    def handle_starttag(self,tag,attrs):
        values=dict(attrs)
        if tag in ('script','style'):self.skip+=1
        if tag=='a':self.links.append(values.get('href'))
        if tag in ('form','input','select','textarea','option'):
            self.fields.append((tag,tuple(sorted((key,value) for key,value in attrs if key not in ('class','style')))))
        if tag in ('img','video','source'):
            self.media.append((tag,tuple((key,values.get(key)) for key in ('src','srcset','poster','alt','controls','preload') if key in values)))
    def handle_endtag(self,tag):
        if tag in ('script','style'):self.skip-=1
    def handle_data(self,data):
        if not self.skip:self.text.append(data)
    def signature(self):
        return {'wording':re.sub(r'\s+',' ',' '.join(self.text)).strip(),'links':self.links,'form fields':self.fields,'media identities':self.media}

count=0
for file in sorted(ROOT.glob('*.html')):
    original=subprocess.check_output(['git','show',f'{REFERENCE}:{file.name}'],cwd=ROOT,text=True)
    before=Content(original).signature();after=Content(file.read_text()).signature()
    for key in before:
        assert before[key]==after[key],f'{file.name}: {key} changed'
    count+=1
for path in ('data/projects.json','data/products.json','assets/experience-core.js','api/contact.php'):
    original=subprocess.check_output(['git','show',f'{REFERENCE}:{path}'],cwd=ROOT)
    assert original==(ROOT/path).read_bytes(),f'{path}: protected data or behavior changed'
print(f'{count} pages: wording, navigation, form fields and media preserved against {REFERENCE}; project facts and contact backend unchanged.')
