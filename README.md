# LEDDISPLAY

Türkçe, duyarlı ve çok sayfalı LED ekran kurumsal web sitesi. Üretim çıktısı düz HTML/CSS/JavaScript'tir; Plesk sunucusunda Node.js veya veritabanı gerekmez. Görseller özgün SVG ve CSS konseptleridir, gerçek müşteri projesi olarak sunulmaz.

## Yerel geliştirme

Node.js 22+ ve Python 3 kullanın. Harici npm bağımlılığı yoktur.

```sh
cd /workspace/leddisplay
npm run build
npm test
npm run dev
```

Kaynak sayfa içerikleri `scripts/build.mjs`, ortak stiller `assets/style.css`, etkileşimler `assets/app.js` içindedir. HTML çıktıları depoda tutulur; kaynak değişikliklerinden sonra build çalıştırın. Google Fonts erişilemezse sistem yazı tipi kullanılır. Hareket azaltma tercihi desteklenir.

## Plesk ve DNS

1. Natro'da kök alan adı (`@`) A kaydı `194.36.87.191` olmalı. `www` için kök alan adına CNAME veya aynı IP'ye A kaydı tanımlayın. Çakışan eski A/AAAA kayıtlarını kontrol edin. Bu oturumda DNS veya sunucu sahipliği doğrulanmadı.
2. Plesk'te alan adının hosting ayarlarında belge kökünü `httpdocs` olarak seçin. DNS yayılımından sonra Let's Encrypt ile hem kök alan adına hem `www` adına sertifika alın. HTTPS ve tercih edilen alan adına yönlendirmeyi Plesk'te etkinleştirin.
3. Git ekranında **Remote repository** ve `https://github.com/Mchdozr/leddisplay.git` doğrudur. Plesk'te `main` dalını seçin. Güncellemeleri almak için Pull, yayımlamak için Deploy kullanın.
4. İlk yayın için **Manual** dağıtım önerilir. Deployment directory `/httpdocs` olabilir: hazır HTML dosyaları deponun kökünde bulunur. Plesk'te Node.js ve post-deployment build gerekmez.
5. Özel depo için tercih edilen yöntem Plesk'in ürettiği SSH anahtarının GitHub'da bu depoya salt okunur deploy key olarak eklenmesi ve SSH URL kullanılmasıdır. HTTPS kimlik doğrulamasında GitHub hesap şifresi yerine sınırlı yetkili token gerekir; tokenı koda veya sohbet içine yazmayın.
6. Automatic dağıtım, Plesk deposuna yeni commit çekildiğinde dosyaları yayımlar. GitHub push sonrasında otomatik çekim için Plesk'in webhook URL'sini GitHub webhook ayarına ekleyin; yalnızca Automatic seçmek GitHub push bildirimini kurmaz.
7. `scripts/`, `package.json` ve README dağıtım dışında bırakılabiliyorsa hariç tutun. Apache `.htaccess` paket manifesti ve README erişimini kapatır; Nginx-only kurulumlarda eşdeğer kurallar Plesk üzerinden ayrıca uygulanmalıdır.
8. Ana sayfayı, çözümleri, menüyü, iletişim indirmesini, SSL yönlendirmelerini ve gerçek bir bulunamayan URL'nin 404 durumunu canlı ortamda kontrol edin. Python geliştirme sunucusu Apache `.htaccess` kurallarını çalıştırmaz.

## Sayfalar

Ana sayfa; filtrelenebilir 31 kayıtlı ürün/modül ve kabin kataloğu, 31 ürün detay sayfası; kurumsal; çözümler; iç mekân, dış mekân, etkinlik, şeffaf, video wall ve özel LED çözüm detayları; sektörler; proje yaklaşımı; bilgi merkezi; iletişim; gizlilik; çerez kullanımı; 404.

## Yayın öncesi içerik gereksinimleri

- İşletme unvanı, telefon, e-posta, açık adres, hizmet kapsamı ve doğrulanmış firma geçmişi eklenmeli.
- Kuruluş yılı, müşteri logoları, referans projeler, sertifikalar, garantiler ve teknik ürün değerleri doğrulanmadan kullanılmamalı.
- İletişim formu **gönderim yapmaz**: tarayıcıda proje özeti indirir. Gerçek başvuru almak için sunucu tarafında doğrulama, istek sınırlama, spam koruması ve e-posta/CRM teslimatı kurulmalı; başarılı teslimat test edilmeli.
- Gizlilik sayfası mevcut teknik davranışı anlatır; işletmeye özgü KVKK metni ve veri sorumlusu bilgileri tamamlanmalıdır.
- Proje yaklaşımı bölümü gerçek referans portföyü değildir. Görseller kavramsaldır.

## Doğrulama

`npm test` tüm üretilmiş sayfalarda başlık, açıklama ve yerel dosya/bağlantı bütünlüğünü denetler. Kurulum oturumunda ayrıca Chromium ile tüm sayfaların 1440, 768 ve 390 piksel genişliklerinde açılması, yatay taşma, mobil menü, JavaScript hataları ve indirilen form dosyasının içeriği kontrol edilmiştir. Canlı DNS, Plesk dağıtımı ve gerçek iletişim teslimatı bu testlerin kapsamı dışındadır.

## Sağlanan ürün föyleri

`data/products.json`, iki spec arşivinden çıkarılan 31 benzersiz föyün verilerini tutar: 26 LED modül ve 5 kabin/ürün ailesi. Grand Air kabinleri birden fazla boyut ve piksel aralığı içerir; varyantlar ayrı tabloda gösterilir. `assets/spec/` özgün PDF'leri, `assets/products/` PDF'lerden değiştirilmeden çıkarılan fotoğrafları içerir. Zemin ekranı için belgede fotoğraf çıkarılamadığından açıkça temsilî çizim kullanılır.

Kaynaklar ve tutarsızlıklar `DATA_SOURCES.md` içinde kayıtlıdır. Özellikle P0.93 dinamik/fiziksel aralık ayrımı, P3.91 zemin IP sınıfı çelişkisi ve Grand Air dış mekân parlaklık seçenekleri üretici teyidi gerektirir. Sayfalardaki teknik notlar bu ayrımları korur. İki birebir kopya SHA-256 ile ayıklanmıştır.

## Plesk yayın paketi

```sh
npm run package
```

`/workspace/leddisplay-plesk.zip` oluşur. Paket yalnızca 48 HTML sayfasını (404 dâhil), varlıkları, PDF'leri, sitemap/robots dosyalarını ve `.htaccess` içerir; kaynak scriptler veya geliştirici belgeleri eklenmez. Plesk Dosya Yöneticisi ile `httpdocs` içine açılabilir. Var olan canlı dosyalar önce yedeklenmelidir. Bu paketin oluşturulması sunucuya yükleme veya GitHub'a push anlamına gelmez.

`npm test` ayrıca ürünlerin benzersizliğini, PDF başlıklarını, fotoğraf yollarını, kaynak SHA-256 özetlerini ve ürün-detay eşleşmelerini doğrular. Tam tarayıcı kontrolü için Python Playwright ve Chromium bulunan ortamda `python3 scripts/browser-check.py` çalıştırılabilir; önce `npm run dev` başlatılmalıdır.

## Kurumsal ana sayfa

Ana sayfa kaynağı `scripts/home.mjs` içinde bulunur; `scripts/build.mjs` tarafından üretilir. Ürün vitrini sekmeleri, altı kombinasyonlu çözüm seçici, beş ürünlü teknik karşılaştırma, satış/kiralama/montaj/destek hizmetleri, uygulama senaryoları, sektörler, süreç, rehberler ve SSS bölümlerini içerir. Sayısal ürün ve seri bilgileri mevcut katalog kapsamını ifade eder; firma yaşı veya tamamlanan proje sayısı değildir.

`assets/corporate-hero.webp` ve `assets/application-scenes.webp` bu tasarım için üretilmiş temsilî görsellerdir. Gerçek müşteri projesi veya firma referansı olarak kullanılmaz. Uygulama kartları bunu açıklar. Müşteri adları, referans fotoğrafları ve proje bilgileri doğrulandığında gerçek portföy ayrı içerikle eklenmelidir.

CSS ve JavaScript dosya adreslerinde içerik hash'i bulunur; Pull/Deploy sonrasında güncellemelerin eski tarayıcı önbelleği nedeniyle kaybolmasını önler. Görseller WebP olarak optimize edilmiştir. `npm run test:browser`, temel sayfa/katalog testlerine ek olarak ana sayfa sekmelerini ve çözüm seçiciyi de doğrular.

## İçerik yoğunluğu, hareket ve alt menü

Ana sayfada H/GOB/Q-Air/Grand Air ailelerini açıklayan ek ürün vitrini ile altı maddelik kurulum kontrol listesi ve açılır teknik destek başlıkları bulunur. Bölüm ve kart girişleri görünür içerik üzerine Web Animations API ile uygulanır; JavaScript kapalıyken de içerik görünür kalır. `prefers-reduced-motion` etkinse giriş animasyonları atlanır; tercih sonradan değişirse çalışan giriş animasyonları iptal edilir. Kaydırma göstergesi ve sayfa başına dönüş bağlantısı uzun sayfada gezinmeyi kolaylaştırır.

Tüm sayfaların ortak footer kaynağı `scripts/footer.mjs` içindedir. Hizmetlere hızlı erişim, ürün çözümleri, ürün aileleri, kurumsal/hizmet menüsü, bilgi merkezi, sektörler, teknik katalog ve yasal bağlantıları içerir. Telefon veya e-posta gibi doğrulanmamış firma bilgileri eklenmemiştir. Bölüm bağlantıları `npm test` ile gerçek hedef kimliklerine karşı doğrulanır. Stil ve JS değişiklikleri için HTML çıktısını `npm run build` ile yenileyin.
