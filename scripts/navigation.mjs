export function renderNavigation(slug){
 const link=(title,href,current=false)=>`<a href="${href}"${current?' aria-current="page"':''}>${title}</a>`;
 return `${link('Anasayfa','/',slug==='index')}${[['projeler','Projeler'],['kurumsal','Kurumsal'],['cozumler','Çözümler'],['sektorler','Sektörler'],['proje-yaklasimimiz','Proje süreci'],['bilgi-merkezi','Bilgi merkezi'],['iletisim','İletişim']].map(([s,t])=>link(t,`/${s}`,slug===s||(s==='projeler'&&slug.startsWith('proje-')&&slug!=='proje-yaklasimimiz'))).join('')}`;
}
