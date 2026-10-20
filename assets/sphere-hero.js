// Animate only a clipped highlight on the LED surface; the photograph stays still.
const root=document.querySelector('[data-sphere-hero]');
if(root){
 const image=root.querySelector('.corporate-hero-visual>img');
 const visual=image.parentElement;
 const glow=visual.querySelector('.hero-led-glow');
 const button=root.querySelector('.sphere-motion-toggle');
 const label=button.querySelector('span');
 const preference=matchMedia('(prefers-reduced-motion: reduce)');
 let paused=preference.matches,inView=true;
 function align(){
  if(!image.naturalWidth)return;
  const width=visual.clientWidth,height=visual.clientHeight;
  const scale=Math.max(width/image.naturalWidth,height/image.naturalHeight);
  const renderedWidth=image.naturalWidth*scale,renderedHeight=image.naturalHeight*scale;
  const [positionX,positionY]=getComputedStyle(image).objectPosition.split(' ').map(v=>parseFloat(v)/100);
  const left=(width-renderedWidth)*positionX,top=(height-renderedHeight)*positionY;
  // Sphere bounds in the generated composition; the brand plaque is outside this mask.
  Object.assign(glow.style,{left:`${left+renderedWidth*.490}px`,top:`${top+renderedHeight*.060}px`,width:`${renderedWidth*.425}px`,height:`${renderedHeight*.69}px`});
 }
 function update(){
  root.classList.toggle('sphere-is-still',paused||!inView||document.hidden);
  label.textContent=paused?'Hareketi başlat':'Hareketi durdur';
  button.setAttribute('aria-pressed',String(paused));
  button.setAttribute('aria-label',`LED ekran görselindeki ${paused?'hareketi başlat':'hareketi durdur'}`);
 }
 root.classList.add('sphere-motion-ready');button.hidden=false;
 image.addEventListener('load',align);
 new ResizeObserver(align).observe(visual);
 new IntersectionObserver(entries=>{inView=entries[0].isIntersecting;update()},{threshold:.05}).observe(root);
 document.addEventListener('visibilitychange',update);
 preference.addEventListener('change',()=>{paused=preference.matches;update()});
 button.addEventListener('click',()=>{paused=!paused;update()});
 align();update();
}
