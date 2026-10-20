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
