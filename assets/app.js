const toggle=document.querySelector('.menu-toggle');const navigation=document.querySelector('.navlinks');toggle?.addEventListener('click',()=>{const open=toggle.getAttribute('aria-expanded')!=='true';toggle.setAttribute('aria-expanded',String(open));toggle.setAttribute('aria-label',open?'Menüyü kapat':'Menüyü aç');navigation.classList.toggle('open',open)});document.addEventListener('keydown',e=>{if(e.key==='Escape'){navigation?.classList.remove('open');toggle?.setAttribute('aria-expanded','false');toggle?.setAttribute('aria-label','Menüyü aç')}});
document.querySelectorAll('.reveal').forEach(el=>el.classList.add('visible'));

const projectForm=document.querySelector('#project-form');
if(projectForm){
 const boxes=[...projectForm.querySelectorAll('input[name=products]')];
 const updateSelection=()=>{const count=boxes.filter(b=>b.checked).length;document.querySelector('#selected-products-count').textContent=count?`${count} ürün seçildi.`:'Henüz ürün seçilmedi.';const list=document.querySelector('#selected-products-list');list.replaceChildren();boxes.filter(b=>b.checked).forEach(box=>{const remove=document.createElement('button');remove.type='button';remove.textContent=box.value+' ×';remove.setAttribute('aria-label',box.value+' seçimini kaldır');remove.addEventListener('click',()=>{box.checked=false;updateSelection()});list.append(remove)})};
 boxes.forEach(box=>box.addEventListener('change',updateSelection));
 const requested=new URLSearchParams(location.search).get('urun');boxes.forEach(box=>{if(box.value===requested)box.checked=true});updateSelection();
 document.querySelector('#picker-search').addEventListener('input',e=>{const term=e.target.value.trim().toLocaleLowerCase('tr');let total=0;projectForm.querySelectorAll('.product-option').forEach(option=>{option.hidden=!option.dataset.productSearch.includes(term);if(!option.hidden)total++});projectForm.querySelectorAll('.picker-category').forEach(group=>{group.hidden=![...group.querySelectorAll('.product-option')].some(option=>!option.hidden)});document.querySelector('#picker-empty').hidden=total>0});
 projectForm.addEventListener('submit',e=>{
  e.preventDefault();const data=new FormData(projectForm);const labels={name:'Ad Soyad',company:'Firma',email:'E-posta',phone:'Telefon',solution:'Talep türü'};
  const content='LEDDISPLAY — PROJE TALEBİ\n\n'+Object.entries(labels).map(([key,label])=>`${label}: ${data.get(key)||'Belirtilmedi'}`).join('\n')+'\n\nSeçilen ürünler:\n'+(data.getAll('products').join('\n')||'Henüz ürün seçilmedi')+'\n\nProje açıklaması:\n'+data.get('message');
  const status=document.querySelector('#form-status');
  if(e.submitter?.value==='download'){const href=URL.createObjectURL(new Blob(['\ufeff'+content],{type:'text/plain;charset=utf-8'}));const link=document.createElement('a');link.href=href;link.download='leddisplay-proje-ozeti.txt';link.click();setTimeout(()=>URL.revokeObjectURL(href),1000);status.textContent='Seçtiğiniz ürünlerle proje özetiniz indirildi. Bilgileriniz sunucuya gönderilmedi.';return}
  const draft=document.createElement('a');draft.id='email-draft';draft.href='mailto:info@leddisplay.com.tr?subject='+encodeURIComponent('LEDDISPLAY — '+data.get('solution'))+'&body='+encodeURIComponent(content);draft.textContent='E-posta taslağını yeniden aç';status.replaceChildren('Taslağınız hazır. Gönderimi e-posta uygulamanızdan tamamlayın. ',draft);draft.click();
 });
}
const filters=document.querySelector('#catalog-filters');if(filters){
 const search=document.querySelector('#product-search');const environment=document.querySelector('#environment-filter');const series=document.querySelector('#series-filter');const cards=[...document.querySelectorAll('.catalog-grid .product-card')];const categoryButtons=[...document.querySelectorAll('[data-catalog-series]')];
 function update(){const term=search.value.trim().toLocaleLowerCase('tr');let count=0;cards.forEach(card=>{const show=(!term||card.dataset.search.includes(term))&&(!environment.value||card.dataset.environment===environment.value)&&(!series.value||card.dataset.series===series.value);card.hidden=!show;if(show){count++;card.classList.add('visible')}});categoryButtons.forEach(button=>{const active=button.dataset.catalogSeries===series.value;button.classList.toggle('active',active);button.setAttribute('aria-pressed',String(active))});document.querySelector('#product-count').textContent=`${count} ürün listeleniyor.`;document.querySelector('#no-products').hidden=count>0}
 categoryButtons.forEach(button=>button.addEventListener('click',()=>{series.value=button.dataset.catalogSeries;update()}));
 const params=new URLSearchParams(location.search);const initialSeries=params.get('seri');if([...series.options].some(o=>o.value===initialSeries))series.value=initialSeries;environment.value=params.get('ortam')==='ic'?'İç mekân':params.get('ortam')==='dis'?'Dış mekân':'';
 filters.addEventListener('input',update);filters.addEventListener('change',update);filters.addEventListener('submit',e=>e.preventDefault());filters.addEventListener('reset',()=>setTimeout(update,0));update();
}

const featuredFilters=document.querySelectorAll('[data-feature-filter]');featuredFilters.forEach(button=>button.addEventListener('click',()=>{const filter=button.dataset.featureFilter;featuredFilters.forEach(b=>{const active=b===button;b.classList.toggle('active',active);b.setAttribute('aria-pressed',String(active))});document.querySelectorAll('.featured-product').forEach(card=>{card.hidden=!(filter==='all'||card.dataset.homeEnvironment===filter||(filter==='rental'&&['rental','esnek-kabin'].includes(card.dataset.homeSeries)))})}));
const finder=document.querySelector('#solution-finder');if(finder){function updateFinder(){const place=finder.elements.place.value;const project=finder.elements.project.value;let title,description,href;if(project==='curved'){title='Esnek ve özel LED çözümleri';description=place==='outdoor'?'Dış mekânda kavisli uygulama için ürün uygunluğu, koruma ve taşıyıcı sistem ayrıca projelendirilmelidir.':'İç mekân kavisli yüzeylerde esnek Q modül ve Q-Air kabin seçeneklerini değerlendirin.';href='/ozel-led-cozumleri.html'}else if(project==='rental'){title=place==='outdoor'?'Dış mekân kiralık LED kabin':'İç mekân kiralık LED kabin';description='Grand Air kabinleri; sahne ölçüsü, görüş mesafesi, içerik ve kamera kullanımıyla birlikte değerlendirin.';href='/urun-grand-air-'+(place==='outdoor'?'dis':'ic')+'-mekan.html'}else{title=place==='outdoor'?'Dış mekân LED ekran':'İç mekân LED ekran';description=place==='outdoor'?'Ortam ışığı, ön/arka koruma, taşıyıcı koşulları ve servis erişimini birlikte planlayın.':'Yakın izleme mesafesi, piksel aralığı ve mekân ışığını birlikte değerlendirin.';href=place==='outdoor'?'/dis-mekan-led-ekran.html':'/ic-mekan-led-ekran.html'}document.querySelector('#finder-title').textContent=title;document.querySelector('#finder-description').textContent=description;document.querySelector('#finder-link').href=href}finder.addEventListener('change',updateFinder);finder.addEventListener('submit',e=>e.preventDefault())}

// Scroll entries translate upward at full opacity; reduced-motion preferences skip movement.
const motionPreference=window.matchMedia('(prefers-reduced-motion: reduce)');
function animateEntry(element,delay=0){if(motionPreference.matches||!element.animate)return;return element.animate([{transform:'translateY(18px)'},{transform:'translateY(0)'}],{duration:560,delay,easing:'cubic-bezier(.2,.65,.3,1)'})}
const homeRoot=document.querySelector('.home-main');
if(homeRoot){
 const targets=homeRoot.querySelectorAll('.home-heading,.solution-tile,.featured-product,.series-card,.service-card,.showcase-card,.technical-points>div,.sector-links>a,.process-grid>div,.knowledge-card,.readiness-checklist,.support-topic');
 targets.forEach(el=>el.setAttribute('data-entry-motion',''));
 if('IntersectionObserver'in window){const entries=new IntersectionObserver(items=>{items.forEach(item=>{if(!item.isIntersecting)return;item.target.classList.add('motion-seen');animateEntry(item.target,Math.min([...item.target.parentElement.children].indexOf(item.target)%4,3)*45);entries.unobserve(item.target)})},{threshold:.12,rootMargin:'0px 0px -24px 0px'});targets.forEach(el=>entries.observe(el))}
 const progress=homeRoot.querySelector('.reading-progress>span');const back=homeRoot.querySelector('.back-to-top');let scrollPending=false;
 function updateScrollUI(){const range=document.documentElement.scrollHeight-innerHeight;progress.style.transform=`scaleX(${range>0?Math.min(1,Math.max(0,scrollY/range)):0})`;back.classList.toggle('is-visible',scrollY>700);document.querySelector('.header')?.classList.toggle('is-scrolled',scrollY>30);scrollPending=false}
 function queueScrollUI(){if(!scrollPending){scrollPending=true;requestAnimationFrame(updateScrollUI)}}
 addEventListener('scroll',queueScrollUI,{passive:true});addEventListener('resize',queueScrollUI);updateScrollUI();
 featuredFilters.forEach(button=>button.addEventListener('click',()=>{homeRoot.querySelectorAll('.featured-product:not([hidden])').forEach((el,i)=>animateEntry(el,(i%4)*35));queueScrollUI()}));
 finder?.addEventListener('change',()=>animateEntry(document.querySelector('.finder-result')));
 homeRoot.querySelectorAll('details').forEach(details=>details.addEventListener('toggle',()=>{if(details.open){const content=details.querySelector('p');if(content)animateEntry(content)}queueScrollUI()}));
 motionPreference.addEventListener('change',()=>{if(motionPreference.matches)homeRoot.querySelectorAll('[data-entry-motion],.finder-result,details p').forEach(el=>el.getAnimations().forEach(animation=>animation.cancel()))});
}


// Product navigation supports hover, keyboard, touch and an explicit mobile toggle.
const productGroup=document.querySelector('.nav-product-group');const productToggle=document.querySelector('.product-menu-toggle');
if(productGroup&&productToggle){
 document.documentElement.classList.add('navigation-ready');
 const desktop=()=>matchMedia('(min-width:1101px)').matches;
 function setProductMenu(open){productGroup.classList.toggle('is-open',open);productToggle.setAttribute('aria-expanded',String(open));productToggle.setAttribute('aria-label',open?'Ürün kategorilerini kapat':'Ürün kategorilerini aç')}
 productToggle.addEventListener('click',()=>setProductMenu(productToggle.getAttribute('aria-expanded')!=='true'));
 productGroup.addEventListener('pointerenter',()=>{if(desktop())setProductMenu(true)});
 productGroup.addEventListener('pointerleave',()=>{if(desktop()&&!productGroup.contains(document.activeElement))setProductMenu(false)});
 productGroup.addEventListener('focusout',e=>{if(!productGroup.contains(e.relatedTarget))setProductMenu(false)});
 document.addEventListener('click',e=>{if(!productGroup.contains(e.target))setProductMenu(false)});
 document.addEventListener('keydown',e=>{if(e.key==='Escape'&&productGroup.classList.contains('is-open')){setProductMenu(false);productToggle.focus()}});
 toggle?.addEventListener('click',()=>{if(toggle.getAttribute('aria-expanded')==='false')setProductMenu(false)});
}
if(!homeRoot&&'IntersectionObserver'in window){const entries=new IntersectionObserver(items=>items.forEach(item=>{if(item.isIntersecting){animateEntry(item.target);entries.unobserve(item.target)}}),{threshold:.1});document.querySelectorAll('.reveal').forEach(el=>entries.observe(el))}

motionPreference.addEventListener('change',()=>{if(motionPreference.matches)document.querySelectorAll('.reveal').forEach(el=>el.getAnimations().forEach(animation=>animation.cancel()))});
