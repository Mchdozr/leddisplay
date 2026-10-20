import {sizeScreen,comparisonRows} from './experience-core.js';
const $=(selector,root=document)=>root.querySelector(selector);
const $$=(selector,root=document)=>[...root.querySelectorAll(selector)];
const motion=matchMedia('(prefers-reduced-motion: reduce)');
const number=(v,max=2)=>Number(v).toLocaleString('tr-TR',{maximumFractionDigits:max});
const escape=value=>String(value).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('"','&quot;').replaceAll("'",'&#39;');
let dataPromise;
function getCatalog(){return dataPromise??=fetch('/assets/catalog-experience.json').then(response=>{if(!response.ok)throw new Error('Ürün verileri şu anda yüklenemedi.');return response.json()}).catch(error=>{dataPromise=null;throw error})}
function dialogEvents(dialog){
 dialog.addEventListener('click',event=>{if(event.target===dialog){const b=dialog.getBoundingClientRect();if(event.clientX<b.left||event.clientX>b.right||event.clientY<b.top||event.clientY>b.bottom)dialog.close()}});
 dialog.addEventListener('close',()=>document.documentElement.classList.remove('experience-dialog-open'));
 $$('[data-close-dialog]',dialog).forEach(button=>button.addEventListener('click',()=>dialog.close()));
}
function openDialog(dialog){dialog.showModal();document.documentElement.classList.add('experience-dialog-open')}

// Native same-origin view transitions. Normal links, browser history and downloads remain native.
// Browsers may cancel snapshots on fast navigation or a motion-preference change.
// Settle their lifecycle promises so cancellation cannot become an unhandled rejection.
function settleViewTransition(event){const transition=event.viewTransition;if(!transition)return;for(const key of ['ready','finished','updateCallbackDone'])transition[key]?.catch(()=>{});if(motion.matches)transition.skipTransition()}
addEventListener('pageswap',settleViewTransition);addEventListener('pagereveal',settleViewTransition);
document.addEventListener('click',event=>{
 const link=event.target.closest('a[href]');if(!link||event.button!==0||event.ctrlKey||event.metaKey||event.shiftKey||event.altKey||link.target||link.hasAttribute('download'))return;
 const url=new URL(link.href);if(url.origin!==location.origin||!url.pathname.startsWith('/urun-')||motion.matches)return;
 $$('[style*="view-transition-name"]').forEach(el=>el.style.viewTransitionName='none');
 const image=$('img',link);if(image){const stage=$('#product-main-image');if(stage)stage.style.viewTransitionName='none';image.style.viewTransitionName='product-visual'}
});
addEventListener('pageshow',()=>{$$('[style*="view-transition-name"]').forEach(el=>el.style.removeProperty('view-transition-name'))});

// A procedural LED film: no external player, autoplay sound or video download.
const hero=$('#hero-motion');
if(hero){
 const context=hero.getContext('2d');const visual=hero.parentElement;const pause=$('#hero-motion-toggle');const scene=$('#hero-scene-toggle');let paused=motion.matches,architecture=false,inView=false,frame=0,time=0,last=0;
 function resize(){const r=visual.getBoundingClientRect(),dpr=Math.min(devicePixelRatio||1,1.5);hero.width=Math.round(r.width*dpr);hero.height=Math.round(r.height*dpr);context?.setTransform(dpr,0,0,dpr,0,0);paint(time)}
 function paint(t){if(!context)return;const w=visual.clientWidth,h=visual.clientHeight;context.fillStyle='#071426';context.fillRect(0,0,w,h);
  const gradient=context.createRadialGradient(w*.7,h*.35,5,w*.5,h*.5,w*.85);gradient.addColorStop(0,'#133D57');gradient.addColorStop(1,'#071426');context.fillStyle=gradient;context.fillRect(0,0,w,h);
  for(let y=0;y<h;y+=16){for(let x=0;x<w;x+=16){context.fillStyle='rgba(133,166,193,.09)';context.fillRect(x,y,1,1)}}
  const colors=['#2479CC','#38B7CB','#F57937','#FDBA74'];
  colors.forEach((color,index)=>{context.beginPath();for(let x=-20;x<w+20;x+=4){const y=h*.43+Math.sin(x/w*5.7+t*.65+index*.42)*h*.13+Math.sin(x/w*10-t*.45)*h*.035+index*9;x===-20?context.moveTo(x,y):context.lineTo(x,y)}context.strokeStyle=color;context.shadowColor=color;context.shadowBlur=22;context.lineWidth=2.6;context.stroke();context.shadowBlur=0;
   for(let x=0;x<w;x+=8){const y=h*.43+Math.sin(x/w*5.7+t*.65+index*.42)*h*.13+Math.sin(x/w*10-t*.45)*h*.035+index*9;context.fillStyle=color;context.globalAlpha=.45;context.fillRect(x,y+12+Math.sin(x*.03+t)*13,1.6,1.6);context.globalAlpha=1}
  });
  context.fillStyle='rgba(235,242,249,.65)';context.font='10px Arial';
 }
 function tick(now){frame=0;if(paused||architecture||!inView||document.hidden)return;if(last)time+=Math.min((now-last)/1000,.04);last=now;paint(time);frame=requestAnimationFrame(tick)}
 function update(){cancelAnimationFrame(frame);frame=0;last=0;pause.textContent=paused?'Hareketi başlat':'Hareketi durdur';pause.setAttribute('aria-pressed',String(paused));scene.setAttribute('aria-pressed',String(architecture));scene.textContent=architecture?'Dijital yüzey':'Mimari görünüm';visual.classList.toggle('hero-architecture',architecture);$('.visual-caption strong',visual).textContent=architecture?'Şehrin yeni\nodak noktası.':'Görüntünün\nyeni ritmi.';$('.visual-caption small',visual).textContent=architecture?'Temsilî uygulama görseli':'Gerçek zamanlı dijital görselleştirme';if(!paused&&!architecture&&inView&&!document.hidden)frame=requestAnimationFrame(tick)}
 if(context){visual.classList.add('hero-motion-ready');$('.hero-motion-controls').hidden=false;resize();new ResizeObserver(resize).observe(visual);new IntersectionObserver(entries=>{inView=entries[0].isIntersecting;update()},{threshold:.05}).observe(visual);pause.addEventListener('click',()=>{paused=!paused;update()});scene.addEventListener('click',()=>{architecture=!architecture;update()});document.addEventListener('visibilitychange',update);motion.addEventListener('change',()=>{if(motion.matches)paused=true;update()})}
}

// Pin the complete stage inside the tall section; only the inner track travels.
const showcase=document.querySelector('.showcase-section');
if(showcase){
 const stage=$('.showcase-stage',showcase),viewport=$('.showcase-viewport',showcase),track=$('.showcase-grid',showcase),cards=$$('.showcase-card',showcase),steps=$$('[data-project-step]',showcase);
 let distance=0,start=0,raf=0,enabled=false,active=-1;
 const update=()=>{
  if(!enabled)return;
  const progress=Math.max(0,Math.min(1,(scrollY-start)/Math.max(1,distance)));
  track.style.transform=`translate3d(${-distance*progress}px,0,0)`;
  showcase.style.setProperty('--project-progress',progress);
  const index=Math.round(progress*(cards.length-1));
  if(index!==active){active=index;cards.forEach((card,i)=>card.classList.toggle('is-current',i===index));steps.forEach((step,i)=>{if(i===index)step.setAttribute('aria-current','step');else step.removeAttribute('aria-current')});}
 };
 const layout=()=>{
  enabled=innerWidth>=901&&innerHeight>=600&&!motion.matches;
  showcase.classList.toggle('showcase-pinned',enabled);
  if(!enabled){track.style.transform='';showcase.style.height='';showcase.style.removeProperty('--project-progress');cards.forEach(card=>card.classList.remove('is-current'));active=-1;return}
  const headerHeight=$('.header').getBoundingClientRect().height;
  showcase.style.setProperty('--project-top',`${headerHeight}px`);
  distance=Math.max(0,track.scrollWidth-viewport.clientWidth);
  start=showcase.getBoundingClientRect().top+scrollY-headerHeight;
  showcase.style.height=`${stage.offsetHeight+distance}px`;
  update();
 };
 const onScroll=()=>{if(raf)return;raf=requestAnimationFrame(()=>{raf=0;update()})};
 steps.forEach((step,index)=>step.addEventListener('click',()=>{if(enabled)scrollTo({top:start+distance*index/(cards.length-1),behavior:'smooth'})}));
 viewport.addEventListener('focusin',event=>{const index=cards.indexOf(event.target.closest('.showcase-card'));if(enabled&&index>=0){viewport.scrollLeft=0;scrollTo({top:start+distance*index/(cards.length-1),behavior:'instant'})}});
 addEventListener('resize',layout);addEventListener('scroll',onScroll,{passive:true});motion.addEventListener('change',layout);document.fonts.ready.then(layout);layout();
}

// Match annotations to the actual object-fit:contain image, including narrow viewports.
function alignHotspots(root,image,overlay){
 const align=()=>{if(!image.naturalWidth)return;const box=image.getBoundingClientRect(),parent=root.getBoundingClientRect(),style=getComputedStyle(image);const left=parseFloat(style.paddingLeft)||0,right=parseFloat(style.paddingRight)||0,top=parseFloat(style.paddingTop)||0,bottom=parseFloat(style.paddingBottom)||0;const availableW=box.width-left-right,availableH=box.height-top-bottom;const scale=Math.min(availableW/image.naturalWidth,availableH/image.naturalHeight),width=image.naturalWidth*scale,height=image.naturalHeight*scale;Object.assign(overlay.style,{left:(box.left-parent.left+left+(availableW-width)/2)+'px',top:(box.top-parent.top+top+(availableH-height)/2)+'px',width:width+'px',height:height+'px',right:'auto',bottom:'auto',maxWidth:'none',margin:'0'});};
 image.addEventListener('load',align);new ResizeObserver(align).observe(root);align();
}
const hotspotDetails=[
 ['Taşıma kolu','Taşıma kolu, kabinin mekanik yapısının bir parçasıdır. Asma ve kaldırma planı için sertifikalı ekipman ve yük hesabı ayrıca gerekir.'],
 ['Kabin birleşimi','Kabinli kurulumda kabinlerin hizası ve bağlantı düzeni görüntü yüzeyinin bütünlüğünü etkiler. Mekanik birleşim ve kilitleme sırası, üretici talimatlarıyla planlanmalıdır.'],
 ['Servis alanı','Bakım erişimi, ekranın kurulumundan önce düşünülmelidir. Grand Air ailesi föyünde önden servis belirtilir; uygulamadaki erişim ve güvenli çalışma alanı ayrıca doğrulanır.'],
 ['Güç ve veri bağlantısı','Güç beslemesi ve kontrol/veri hatları, ekran ölçüsü ve nihai sistem tasarımıyla birlikte planlanır. Bağlantı tipi, gerilim ve hat kapasitesi üretici belgeleriyle doğrulanmalıdır.']
];
function selectHotspot(buttons,description,index){buttons.forEach((button,i)=>button.setAttribute('aria-pressed',String(i===index)));const [title,text]=hotspotDetails[index];$('strong',description).textContent=`0${index+1} / ${title}`;$('p',description).textContent=text}
$$('[data-product-points]').forEach(root=>{alignHotspots($('.points-photo',root),$('.points-photo img',root),$('.detail-hotspots',root));const buttons=$$('[data-detail-hotspot]',root);buttons.forEach((button,i)=>button.addEventListener('click',()=>selectHotspot(buttons,$('.point-detail',root),i)))});
const story=$('.product-story');
if(story){
 alignHotspots($('.story-photo',story),$('#story-image',story),$('.story-hotspots',story));
 const photos=[['/assets/products/grand-air-ic-mekan-front.jpg','Grand Air kabin üretici fotoğrafı'],['/assets/products/esnek-1-86-ic-mekan-back.jpg','Esnek Q1.86 LED ekran üretici fotoğrafı'],['/assets/products/h-1-25-ic-mekan-front.jpg','H1.25 LED ekran üretici fotoğrafı']];let active=0;
 const controls=$$('[data-story-select]',story);const steps=$$('[data-story-step]',story);const spots=$$('[data-hotspot]',story);
 function select(index){active=index;const image=$('#story-image');image.src=photos[index][0];image.alt=photos[index][1];controls.forEach((button,i)=>button.setAttribute('aria-pressed',String(i===index)));steps.forEach((step,i)=>step.classList.toggle('active',i===index));$('.story-hotspots').hidden=index!==0;const description=$('#hotspot-description');if(index===0){selectHotspot(spots,description,Math.max(0,spots.findIndex(button=>button.getAttribute('aria-pressed')==='true')))}else{$('strong',description).textContent=index===1?'02 / Esnek yüzey':'03 / Görüntü ayrıntısı';$('p',description).textContent=index===1?'Esnek LED ekranın uygulama geometrisi ve asgari bükülme yarıçapı üreticiyle doğrulanmalıdır.':'H1.25 LED ekran: 1,25 mm piksel aralığı ve 256 × 128 fiziksel piksel çözünürlüğü. Kamera sonucu nihai sistemle değerlendirilir.';}$('.story-source').textContent='GERÇEK ÜRÜN FOTOĞRAFI / ÜRETİCİ FÖYÜ';if(!motion.matches)image.animate([{transform:'translateY(7px) scale(.98)'},{transform:'translateY(0) scale(1)'}],{duration:400,easing:'cubic-bezier(.22,1,.36,1)'})}
 controls.forEach((button,i)=>button.addEventListener('click',()=>select(i)));
 spots.forEach((button,i)=>button.addEventListener('click',()=>selectHotspot(spots,$('#hotspot-description'),i)));
 let pending=false;function onScroll(){if(pending)return;pending=true;requestAnimationFrame(()=>{pending=false;if(innerWidth<901||motion.matches)return;const center=innerHeight*.55;let closest=0,distance=Infinity;steps.forEach((step,i)=>{const b=step.getBoundingClientRect();const d=Math.abs(b.top+b.height/2-center);if(d<distance){distance=d;closest=i}});const rect=story.getBoundingClientRect();if(rect.top<innerHeight&&rect.bottom>0&&closest!==active)select(closest)})}
 addEventListener('scroll',onScroll,{passive:true});
}

// Compare up to three real products; store only public product identifiers for this tab.
if($('[data-compare-id]')){
 let selected=[];try{const stored=JSON.parse(sessionStorage.getItem('leddisplay-compare')||'[]');if(Array.isArray(stored))selected=stored.filter(v=>typeof v==='string').slice(0,3)}catch{}
 const tray=document.createElement('aside');tray.className='compare-tray';tray.hidden=true;tray.setAttribute('aria-label','Ürün karşılaştırma seçimi');tray.innerHTML='<span id="compare-selection-count" role="status" aria-live="polite"></span><button type="button" id="compare-open">Karşılaştır</button><button type="button" id="compare-clear" aria-label="Karşılaştırma seçimini temizle">×</button><p id="compare-status" role="status" aria-live="polite"></p>';document.body.append(tray);
 const dialog=document.createElement('dialog');dialog.id='compare-dialog';dialog.className='experience-dialog compare-dialog';dialog.innerHTML='<div class="experience-dialog-toolbar"><div><small>ÜRÜNLERİ YAN YANA İNCELEYİN</small><h2 id="compare-title">Ayrıntılar fark yaratır.</h2></div><button type="button" data-close-dialog aria-label="Karşılaştırmayı kapat">Kapat ×</button></div><label class="compare-differences"><input type="checkbox" id="compare-differences"> Yalnızca farkları göster</label><div id="compare-table" class="compare-table"></div><div class="compare-dialog-bottom"><p>Değerler üretici föylerinden aktarılmıştır. Varyantlı ailelerin kesin teknik değerleri ürün sayfasında incelenmelidir.</p><a class="btn" id="compare-quote" href="/iletisim">Seçtiğim ürünleri sorayım <svg class="inline-arrow" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M6 18 18 6M6 6h12v12" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg></a></div>';dialog.setAttribute('aria-labelledby','compare-title');document.body.append(dialog);dialogEvents(dialog);
 function save(){try{sessionStorage.setItem('leddisplay-compare',JSON.stringify(selected))}catch{}}
 function update(){tray.hidden=!selected.length;$('#compare-selection-count').textContent=`${selected.length} / 3 ürün seçildi`;$('#compare-open').disabled=selected.length<2;$$('[data-compare-id]').forEach(button=>{const on=selected.includes(button.dataset.compareId);button.hidden=false;button.setAttribute('aria-pressed',String(on));button.setAttribute('aria-label',button.dataset.compareTitle+': '+(on?'karşılaştırmadan çıkar':'karşılaştırmaya ekle'));button.innerHTML=`<span aria-hidden="true">${on?'✓':'+'}</span> ${on?'Karşılaştırmaya eklendi':'Karşılaştırmaya ekle'}`});save()}
 async function render(){try{const catalog=await getCatalog();const products=selected.map(id=>catalog.find(p=>p.slug===id)).filter(Boolean);if(products.length<2){dialog.close();return}const rows=comparisonRows(products,$('#compare-differences').checked);$('#compare-table').innerHTML=`<table><caption class="sr-only">Seçilen ürünlerin teknik karşılaştırması</caption><thead><tr><th scope="col">Teknik özellik</th>${products.map(p=>`<th scope="col"><button type="button" data-compare-remove="${p.slug}" aria-label="${escape(p.title)} ürününü karşılaştırmadan çıkar">×</button>${p.image?`<img src="${p.image}" alt="" width="180" height="100">`:'<span class="compare-no-photo">Föyde fotoğraf yok</span>'}<a href="/urun-${p.slug}">${escape(p.title)}</a></th>`).join('')}</tr></thead><tbody>${rows.map(row=>`<tr><th scope="row">${row.label}</th>${row.values.map(value=>`<td>${escape(value)}</td>`).join('')}</tr>`).join('')}</tbody></table>${rows.length?'':'<p class="notice">Seçilen ürünlerin bu alanlardaki değerleri aynıdır.</p>'}`;$('#compare-quote').href='/iletisim?'+products.map(p=>'urun='+encodeURIComponent(p.title)).join('&');$$('[data-compare-remove]',dialog).forEach(button=>button.addEventListener('click',()=>{selected=selected.filter(id=>id!==button.dataset.compareRemove);update();render()}))}catch{dialog.close();$('#compare-status').textContent='Ürün verileri yüklenemedi. Lütfen tekrar deneyin.'}}
 $$('[data-compare-id]').forEach(button=>button.addEventListener('click',()=>{const id=button.dataset.compareId;$('#compare-status').textContent='';if(selected.includes(id))selected=selected.filter(value=>value!==id);else if(selected.length<3)selected.push(id);else{$('#compare-status').textContent='En fazla üç ürün karşılaştırabilirsiniz. Önce bir ürünü çıkarın.';return}update()}));
 $('#compare-clear').addEventListener('click',()=>{selected=[];update()});$('#compare-open').addEventListener('click',async()=>{await render();if(selected.length>=2&&$('#compare-table table'))openDialog(dialog)});$('#compare-differences').addEventListener('change',render);
 getCatalog().then(catalog=>{selected=selected.filter(id=>catalog.some(p=>p.slug===id));update()}).catch(()=>{update()});
}

const tools=$('.experience-tools');
if(tools){
 const tabs=$$('[role=tab]',tools);function tab(index){tabs.forEach((button,i)=>{button.setAttribute('aria-selected',String(i===index));button.tabIndex=i===index?0:-1;$('#'+button.getAttribute('aria-controls')).hidden=i!==index});if(index===1)drawPixels()}
 tabs.forEach((button,index)=>{button.addEventListener('click',()=>tab(index));button.addEventListener('keydown',event=>{let next;if(event.key==='ArrowRight')next=(index+1)%tabs.length;if(event.key==='ArrowLeft')next=(index+tabs.length-1)%tabs.length;if(event.key==='Home')next=0;if(event.key==='End')next=tabs.length-1;if(next!==undefined){event.preventDefault();tab(next);tabs[next].focus()}})});
 let options=[];
 async function calculate(){if(!$('#screen-size-form').reportValidity())return;try{if(!options.length)options=(await getCatalog()).flatMap(p=>p.options);const option=options.find(o=>o.id===$('#size-model').value);const result=sizeScreen(option,Number($('#size-width').value),Number($('#size-height').value),$('#size-fit').value);$('#size-error').hidden=true;$('#size-quote').hidden=false;$('#size-result').innerHTML=`<div class="size-result-heading"><span>UYGULANABİLİR GÖRÜNTÜ ALANI</span><strong>${number(result.width,3)} × ${number(result.height,3)} <small>m</small></strong></div><dl class="size-result-metrics"><div><dt>${option.unit==='kabin'?'Kabin':'LED ekran'} adedi</dt><dd>${number(result.total,0)} <small>(${result.columns} × ${result.rows})</small></dd></div><div><dt>Toplam çözünürlük</dt><dd>${result.pixelsX} × ${result.pixelsY} <small>px</small></dd></div><div><dt>Görüntü alanı</dt><dd>${number(result.area)} <small>m²</small></dd></div></dl><p class="tool-note">${escape(option.label)} · ${option.width} × ${option.height} mm / ${option.pixelsX} × ${option.pixelsY} px. ${option.slug==='dinamik-0-93-ic-mekan'?'Çözünürlük fiziksel piksellerle hesaplanmıştır.':''}</p>`;
  const scale=Math.min(640/result.width,250/result.height),w=result.width*scale,h=result.height*scale,x=(720-w)/2,y=(320-h)/2;$('#size-drawing').innerHTML=`<svg viewBox="0 0 720 320" role="img" aria-label="${result.columns} sütun, ${result.rows} sıra; toplam ${result.total} ${option.unit}"><defs><pattern id="unit-grid" width="${w/result.columns}" height="${h/result.rows}" patternUnits="userSpaceOnUse" x="${x}" y="${y}"><rect width="${w/result.columns}" height="${h/result.rows}" fill="#17374D" stroke="#6B879C" stroke-width="0.6"/></pattern></defs><rect x="${x}" y="${y}" width="${w}" height="${h}" fill="url(#unit-grid)" stroke="#F97316" stroke-width="2"/><text x="360" y="305" text-anchor="middle" fill="#9DB0C2" font-size="13">${number(result.width,3)} m × ${number(result.height,3)} m / ${result.columns} × ${result.rows} ${option.unit}</text></svg>`;
  const product=(await getCatalog()).find(p=>p.slug===option.slug);const summary=`${number(result.width,3)} × ${number(result.height,3)} m, ${result.total} ${option.unit}, ${result.pixelsX} × ${result.pixelsY} px; ${option.label}`;$('#size-quote').href='/iletisim?urun='+encodeURIComponent(product.title)+'&olcu='+encodeURIComponent(summary);
 }catch(error){$('#size-error').hidden=false;$('#size-error').textContent=error.message;$('#size-quote').hidden=true;$('#size-result').replaceChildren();$('#size-drawing').replaceChildren()}}
 $('#screen-size-form').addEventListener('submit',event=>{event.preventDefault();calculate()});calculate();
 const pixel=$('#pixel-canvas');const context=pixel.getContext('2d');const source=document.createElement('canvas');source.width=720;source.height=420;const s=source.getContext('2d');const sample=document.createElement('canvas');const sc=sample.getContext('2d');const pitches=[1.25,1.86,2.5,3.91,5,10];
 function drawPixels(){if(!context||!s||!sc)return;const pitch=pitches[Number($('#pixel-pitch').value)],distance=Number($('#pixel-distance').value);$('#pixel-pitch-value').textContent='P'+number(pitch);$('#pixel-distance-value').textContent=number(distance)+' m';$('#pixel-summary').textContent=`P${number(pitch)} / ${number(distance)} m`;const gradient=s.createLinearGradient(0,0,720,420);gradient.addColorStop(0,'#0A192D');gradient.addColorStop(.5,'#0B5C79');gradient.addColorStop(1,'#E46634');s.fillStyle=gradient;s.fillRect(0,0,720,420);
  for(let i=0;i<4;i++){s.beginPath();for(let x=0;x<720;x+=3){const y=190+Math.sin(x*.009+i*.45)*70+i*12;x===0?s.moveTo(x,y):s.lineTo(x,y)}s.strokeStyle=['#6ED5EF','#3D9BDD','#FDBA74','#F97316'][i];s.lineWidth=4;s.stroke()}
  s.fillStyle='#FFFFFF';s.font='bold 72px Arial';s.fillText('leddisplay',48,110);s.font='20px Arial';s.fillText('AYRINTIDA FARK VAR.',52,350);s.fillRect(52,369,180,3);
  const cell=Math.max(1,Math.min(26,pitch*4/distance));sample.width=Math.max(1,Math.round(720/cell));sample.height=Math.max(1,Math.round(420/cell));sc.drawImage(source,0,0,sample.width,sample.height);context.imageSmoothingEnabled=false;context.drawImage(sample,0,0,720,420);
  if(cell>3){context.fillStyle='rgba(4,12,24,.38)';for(let x=0;x<720;x+=cell)context.fillRect(x,0,Math.max(.6,cell*.13),420);for(let y=0;y<420;y+=cell)context.fillRect(0,y,720,Math.max(.6,cell*.13))}
 }
 ['#pixel-pitch','#pixel-distance'].forEach(id=>$(id).addEventListener('input',drawPixels));$$('[data-pixel-preset]').forEach(button=>button.addEventListener('click',()=>{$('#pixel-pitch').value=button.dataset.pixelPreset;drawPixels()}));drawPixels();
}

// Full-screen application gallery. Every scene is explicitly a concept, not a customer reference.
if($('[data-scene-id]')){
 const scenes=[
 {title:'Perakende & showroom',category:'İÇ MEKÂN / DENEYİM',description:'Vitrin, showroom ve marka deneyim alanlarında içerikle bütünleşen LED yüzey yaklaşımı.',image:'/assets/application-scenes.webp',position:'0%',split:true,href:'/ic-mekan-led-ekran',product:'İnce piksel / iç mekân LED'},
 {title:'Sahne & etkinlik',category:'UYGULAMA / SAHNE',description:'Lansman, konferans ve etkinliklerde sahneye göre planlanan LED ekran senaryosu.',image:'/assets/application-scenes.webp',position:'50%',split:true,href:'/etkinlik-led-ekrani',product:'Grand Air / LED kabin'},
 {title:'Kurumsal & mimari',category:'KURUMSAL / VİDEO WALL',description:'Lobi, karşılama ve sunum alanlarında mimariyle birlikte ele alınan görüntüleme yaklaşımı.',image:'/assets/application-scenes.webp',position:'100%',split:true,href:'/led-video-wall',product:'İç mekân LED / video wall'},
 {title:'Şehrin yeni odak noktası',category:'DIŞ MEKÂN / MİMARİ',description:'Bina cephesinde ölçek, izleme yönü ve içerik etkisini bir araya getiren LED ekran konsepti.',image:'/assets/corporate-hero.webp',position:'center',split:false,href:'/dis-mekan-led-ekran',product:'Dış mekân LED / cephe uygulaması'}
 ];
 const dialog=document.createElement('dialog');dialog.id='application-gallery';dialog.className='experience-dialog application-gallery';dialog.setAttribute('aria-labelledby','application-title');dialog.innerHTML='<div class="application-toolbar"><span>LEDDISPLAY / UYGULAMA PERSPEKTİFLERİ</span><button type="button" data-close-dialog aria-label="Uygulama galerisini kapat">Kapat ×</button></div><div class="application-layout"><div class="application-scene" role="img"><span>TEMSİLÎ UYGULAMA / KONSEPT</span></div><div class="application-description"><small id="application-category"></small><h2 id="application-title"></h2><p id="application-description"></p><div class="application-product"><small>İLGİLİ ÇÖZÜM</small><strong id="application-product"></strong></div><a class="btn" id="application-link" href="/cozumler">Çözümü keşfedin <svg class="inline-arrow" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M6 18 18 6M6 6h12v12" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg></a><p class="application-disclosure">Görsel bir tasarım konseptidir. Tamamlanmış müşteri projesi veya referans değildir.</p></div></div><div class="application-controls"><button type="button" id="application-prev" aria-label="Önceki uygulama">← Önceki</button><span id="application-count" role="status" aria-live="polite"></span><button type="button" id="application-next" aria-label="Sonraki uygulama">Sonraki →</button></div>';document.body.append(dialog);dialogEvents(dialog);let index=0;
 function fitScene(){const scene=scenes[index],photo=$('.application-scene',dialog);if(!scene.split)return;const w=photo.clientWidth,h=photo.clientHeight;if(!w||!h)return;const cell=Math.max(w,h),part=parseFloat(scene.position)/50;photo.style.backgroundSize=`${cell*3}px ${cell}px`;photo.style.backgroundPosition=`${-part*cell-(cell-w)/2}px ${-(cell-h)/2}px`;}
 new ResizeObserver(fitScene).observe($('.application-scene',dialog));
 function show(i){index=(i+scenes.length)%scenes.length;const scene=scenes[index];const photo=$('.application-scene',dialog);photo.style.backgroundImage=`url('${scene.image}')`;photo.style.backgroundSize=scene.split?'300% 100%':'cover';photo.style.backgroundPosition=scene.position+' center';photo.setAttribute('aria-label',scene.title+' — temsili uygulama konsepti');$('#application-category').textContent=scene.category;$('#application-title').textContent=scene.title;$('#application-description').textContent=scene.description;$('#application-product').textContent=scene.product;$('#application-link').href=scene.href;$('#application-count').textContent=`0${index+1} / 0${scenes.length}`;fitScene()}
 $$('[data-scene-id]').forEach(button=>button.addEventListener('click',()=>{show(Number(button.dataset.sceneId));openDialog(dialog)}));$('#application-prev').addEventListener('click',()=>show(index-1));$('#application-next').addEventListener('click',()=>show(index+1));dialog.addEventListener('keydown',event=>{if(event.key==='ArrowRight'){event.preventDefault();show(index+1)}if(event.key==='ArrowLeft'){event.preventDefault();show(index-1)}});let pointerX;$('.application-scene',dialog).addEventListener('pointerdown',event=>{pointerX=event.clientX});$('.application-scene',dialog).addEventListener('pointerup',event=>{if(pointerX!==undefined&&Math.abs(event.clientX-pointerX)>60)show(index+(event.clientX<pointerX?1:-1));pointerX=undefined});
}
