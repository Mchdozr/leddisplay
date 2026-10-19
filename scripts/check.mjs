import {readFileSync,readdirSync,existsSync} from 'node:fs';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
const pages=readdirSync('.').filter(f=>f.endsWith('.html'));
assert.equal(pages.length,48);
let links=0;
for(const page of pages){const html=readFileSync(page,'utf8');assert.ok(!html.includes('${'),`${page}: unresolved template expression`);assert.equal((html.match(/<h1>/g)||[]).length,1,`${page}: h1`);assert.match(html,/<html lang="tr">/);assert.match(html,/<meta name="description"/);for(const match of html.matchAll(/(?:href|src)="(\/[^"#]*)"/g)){const path=match[1].split('?')[0];const target=path==='/'?'index.html':path.slice(1);assert.ok(existsSync(target),`${page}: missing ${target}`);links++}}
assert.ok(existsSync('sitemap.xml'));assert.ok(existsSync('robots.txt'));
console.log(`${pages.length} pages validated; ${links} local resource and navigation references resolved.`);

const products=JSON.parse(readFileSync('data/products.json','utf8'));assert.equal(products.length,31);assert.equal(new Set(products.map(p=>p.slug)).size,31);
for(const p of products){if(p.variants){for(const v of p.variants)assert.ok(v.maxPower>v.averagePower)}else assert.ok(Number(p.maxPower)>Number(p.averagePower));assert.ok(existsSync(`assets/spec/${p.slug}.pdf`));assert.ok(readFileSync(`assets/spec/${p.slug}.pdf`).subarray(0,5).toString()==='%PDF-');if(p.image)assert.ok(existsSync(p.image.slice(1)));else assert.equal(p.series,'zemin');const html=readFileSync(`urun-${p.slug}.html`,'utf8');assert.ok(html.includes(p.spec));assert.ok(html.includes(p.refresh));}
console.log('31 product / family records, manufacturer PDFs, images and matching detail pages validated.');

for(const p of products)assert.equal(createHash('sha256').update(readFileSync(`assets/spec/${p.slug}.pdf`)).digest('hex'),p.sourceSha256);
console.log('All source PDF SHA-256 fingerprints match the catalog provenance records.');

// Footer deep links must land on a real page section, including cross-page anchors.
let sectionLinks=0;
for(const page of pages){for(const [,href] of readFileSync(page,'utf8').matchAll(/href="([^"\s]*#[^"\s]+)"/g)){if(!href.startsWith('/')&&!href.startsWith('#'))continue;const target=new URL(href,'https://leddisplay.com.tr/'+page);const file=target.pathname==='/'?'index.html':target.pathname.slice(1);assert.ok(existsSync(file),`${page}: missing anchored page ${file}`);const id=decodeURIComponent(target.hash.slice(1));assert.ok(readFileSync(file,'utf8').includes(`id="${id}"`),`${page}: missing section ${href}`);sectionLinks++;}}
console.log(`${sectionLinks} anchored navigation links verified.`);
