import assert from 'node:assert/strict';
import {readFileSync,readdirSync,existsSync} from 'node:fs';
const projects=JSON.parse(readFileSync('data/projects.json','utf8'));
assert.equal(new Set(projects.map(p=>p.slug)).size,projects.length);
const sitemap=readFileSync('sitemap.xml','utf8');
for(const p of projects){
 const file=`proje-${p.slug}.html`;
 assert.ok(existsSync(file));
 const html=readFileSync(file,'utf8');
 assert.ok(html.includes(p.name));assert.ok(html.includes('Anahtar teslim'));
 assert.ok(sitemap.includes(`/proje-${p.slug}</loc>`));
 for(const path of [p.cover,...p.gallery.map(x=>x.image),...p.videos.flatMap(x=>[x.src,x.poster])])assert.ok(existsSync(path.slice(1)),`${file}: missing ${path}`);
 for(const match of html.matchAll(/<video\b([^>]*)>/g)){assert.match(match[1],/controls/);assert.match(match[1],/preload="none"/);assert.ok(!match[1].includes('autoplay'))}
}
for(const file of readdirSync('.').filter(f=>f.endsWith('.html'))){
 const html=readFileSync(file,'utf8');
 assert.ok(!/(?:href|src|poster)="\/(?:urunler(?:[?"/])|urun-|assets\/(?:products|spec)\/)/i.test(html),`${file}: archived product access`);
 assert.ok(!/kiralama|kiralık|modül|nav-product-group|product-picker|data-compare-id/i.test(html),`${file}: disabled catalog content`);
 assert.ok(!/GKGD.*(?:USD|Birim Fiyat)|IBAN|119CFA6F|LED2026000000001/.test(html),`${file}: private invoice content`);
}
assert.ok(!/\/urun(?:ler|-)/.test(sitemap),'Archived catalog must stay out of sitemap');
assert.deepEqual(JSON.parse(readFileSync('assets/catalog-experience.json','utf8')),[]);
console.log(`${projects.length} real projects: media, deferred video, private-document exclusion and disabled catalog checks passed.`);
