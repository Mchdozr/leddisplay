import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {experienceCatalog} from './experience.mjs';
import {sizeScreen,comparisonRows} from '../assets/experience-core.js';
const catalog=JSON.parse(readFileSync('data/products.json','utf8'));
const data=experienceCatalog(catalog);const options=data.flatMap(p=>p.options);
assert.equal(new Set(options.map(o=>o.id)).size,options.length);
assert.ok(data.find(p=>p.series==='zemin').options.length===0);
const model=options.find(p=>p.id==='h-1-25-ic-mekan');
assert.deepEqual(sizeScreen(model,3.2,1.92),{columns:10,rows:12,total:120,width:3.2,height:1.92,pixelsX:2560,pixelsY:1536,area:6.144});
assert.equal(sizeScreen(model,3.21,1.93).total,143);
assert.equal(sizeScreen(model,3.21,1.93,'at-most').total,120);
assert.throws(()=>sizeScreen(model,.1,.1,'at-most'));
for(const v of [NaN,Infinity,0,-1,31])assert.throws(()=>sizeScreen(model,v,2));
assert.throws(()=>sizeScreen(model,3,21));
assert.throws(()=>sizeScreen(model,3,2,'invalid'));
const cabin=options.find(o=>o.id==='grand-air-ic-mekan-2.604-1000');
assert.equal(cabin.pixelsY,384);assert.equal(cabin.width,500);assert.equal(cabin.height,1000);
assert.deepEqual(sizeScreen(cabin,4,3),{columns:8,rows:3,total:24,width:4,height:3,pixelsX:1536,pixelsY:1152,area:12});
const dynamic=options.find(o=>o.id==='dinamik-0-93-ic-mekan');assert.equal(dynamic.pixelsX,172);assert.equal(dynamic.pixelsY,86);
for(const o of options){
 const result=sizeScreen(o,3.2,1.92);assert.ok(result.width>=3.2-1e-8&&result.height>=1.92-1e-8,o.id);
 const floor=sizeScreen(o,3.2,1.92,'at-most');assert.ok(floor.width<=3.2+1e-8&&floor.height<=1.92+1e-8,o.id);
 assert.ok(result.total===result.columns*result.rows&&Number.isInteger(result.pixelsX));
}
const two=[catalog.find(p=>p.slug==='h-1-25-ic-mekan'),catalog.find(p=>p.slug==='gob-1-86-ic-mekan')];
assert.equal(comparisonRows(two).length,10);assert.ok(comparisonRows(two,true).length<10);assert.ok(comparisonRows(two,true).some(row=>row.label==='Piksel aralığı (mm)'));
assert.equal(comparisonRows([two[0],two[0]],true).length,0);
console.log(`Sizing: ${options.length} verified unit/variant options; exact/floor/ceiling, physical dynamic pixels, cabin variants, invalid input and comparison differences passed.`);
