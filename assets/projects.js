// A native dialog keeps focus, Escape and keyboard navigation accessible.
const projectPhotos=[...document.querySelectorAll('[data-project-photo]')];
if(projectPhotos.length){
 const dialog=document.createElement('dialog');
 dialog.className='project-lightbox';dialog.setAttribute('aria-label','Proje saha görüntüleri');
 dialog.innerHTML='<div class="project-lightbox-toolbar"><span>LEDDISPLAY / GERÇEK SAHA GÖRÜNTÜLERİ</span><button type="button" data-photo-close autofocus aria-label="Görsel galerisini kapat">Kapat ×</button></div><img alt=""><div class="project-lightbox-bottom"><p id="project-photo-caption"></p><div class="project-lightbox-controls"><button type="button" data-photo-prev aria-label="Önceki görsel">←</button><span role="status" aria-live="polite"></span><button type="button" data-photo-next aria-label="Sonraki görsel">→</button></div></div>';
 dialog.setAttribute('aria-describedby','project-photo-caption');document.body.append(dialog);
 let index=0;let trigger;
 const show=i=>{index=(i+projectPhotos.length)%projectPhotos.length;const photo=projectPhotos[index];const img=dialog.querySelector('img');img.src=photo.dataset.projectPhoto;img.alt=photo.dataset.projectAlt;dialog.querySelector('p').textContent=photo.dataset.projectCaption;dialog.querySelector('[role=status]').textContent=`${index+1} / ${projectPhotos.length}`};
 projectPhotos.forEach((button,i)=>button.addEventListener('click',()=>{trigger=button;show(i);dialog.showModal();document.documentElement.classList.add('project-photo-open')}));
 dialog.querySelector('[data-photo-close]').addEventListener('click',()=>dialog.close());
 dialog.querySelector('[data-photo-prev]').addEventListener('click',()=>show(index-1));
 dialog.querySelector('[data-photo-next]').addEventListener('click',()=>show(index+1));
 dialog.addEventListener('keydown',e=>{if(e.key==='ArrowLeft'){e.preventDefault();show(index-1)}if(e.key==='ArrowRight'){e.preventDefault();show(index+1)}});
 dialog.addEventListener('click',e=>{if(e.target!==dialog)return;const r=dialog.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)dialog.close()});
 dialog.addEventListener('close',()=>{document.documentElement.classList.remove('project-photo-open');trigger?.focus({preventScroll:true})});
}
// Loading the page never downloads the project films; play remains user controlled.
document.querySelectorAll('.project-videos video').forEach(video=>video.addEventListener('play',()=>{document.querySelectorAll('.project-videos video').forEach(other=>{if(other!==video)other.pause()})}));

// Progressive archive controls: every project stays available without JavaScript.
const archive=document.querySelector('[data-project-archive]');
if(archive){
 const tools=archive.querySelector('.project-archive-tools');
 const filters=[...archive.querySelectorAll('[data-project-filter]')];
 const cards=[...archive.querySelectorAll('[data-project-group]')];
 const search=archive.querySelector('#project-search');
 const count=archive.querySelector('[data-project-count]');
 const empty=archive.querySelector('.project-no-results');
 const normalize=value=>value.toLocaleLowerCase('tr-TR').normalize('NFD').replace(/[\u0300-\u036f]/g,'').replaceAll('ı','i').replace(/[’']/g,'');
 const searchable=new Map(cards.map(card=>[card,normalize(card.textContent)]));
 let selected='all';
 const update=(save=true)=>{
  const term=normalize(search.value.trim());let total=0;
  cards.forEach(card=>{card.hidden=!(selected==='all'||card.dataset.projectGroup===selected)||!searchable.get(card).includes(term);if(!card.hidden)total++});
  filters.forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.projectFilter===selected)));
  count.textContent=`${total} proje${term||selected!=='all'?' listeleniyor':''}`;
  empty.hidden=total!==0;
  if(save){
   const url=new URL(location.href);
   if(selected==='all')url.searchParams.delete('sektor');else url.searchParams.set('sektor',selected);
   if(search.value.trim())url.searchParams.set('ara',search.value.trim());else url.searchParams.delete('ara');
   history.replaceState(history.state,'',url);
  }
 };
 const restore=()=>{const params=new URLSearchParams(location.search);selected=filters.some(button=>button.dataset.projectFilter===params.get('sektor'))?params.get('sektor'):'all';search.value=(params.get('ara')||'').slice(0,100);update(false)};
 filters.forEach(button=>button.addEventListener('click',()=>{selected=button.dataset.projectFilter;update()}));
 search.addEventListener('input',()=>update());
 search.form.addEventListener('submit',event=>event.preventDefault());
 archive.querySelector('[data-project-reset]').addEventListener('click',()=>{selected='all';search.value='';update();search.focus({preventScroll:true})});
 addEventListener('popstate',restore);
 restore();tools.hidden=false;
}
