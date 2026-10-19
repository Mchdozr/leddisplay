# LEDDISPLAY

Türkçe kurumsal LED ekran sitesi: 48 HTML sayfası, 31 belgeli ürün/kabin ailesi ve PHP üzerinden çalışan iletişim formu. Üretim sunucusunda Node.js veya veritabanı gerekmez. İletişim gönderimi için **PHP 8.1+ ve çalışan yerel posta servisi** gerekir.

## Geliştirme

Node.js 22+, Python 3 ve PHP 8.1+ kullanın. Npm bağımlılığı yoktur.

```sh
cd /workspace/leddisplay
npm run build
npm test
npm run dev
```

`npm run dev` PHP geliştirme sunucusunu 3000 portunda açar. PHP `PATH` içinde değilse bu bulut oturumunda hazırlanmış `/workspace/.tools/leddisplay-php/php` aracını da bulabilir. Yerel posta sistemi olmayan makinelerde gerçek gönderim hata verir; testler güvenli bir yakalama transportu kullanır. PHP geliştirme sunucusunu üretimde kullanmayın.

Kaynaklar:

- `scripts/build.mjs`: iç sayfalar, ürün detayları ve HTML üretimi.
- `scripts/home.mjs`: ana sayfa ve interaktif çözüm seçici.
- `scripts/navigation.mjs`: klavye, hover ve dokunma destekli kategorili üst menü.
- `scripts/footer.mjs`: kompakt masaüstü footer ve mobil açılır gruplar.
- `scripts/product-gallery.mjs`: sabit boyutlu görsel galerisi ve büyütme penceresi.
- `scripts/contact.mjs`: telefon, e-posta ve WhatsApp bağlantıları.
- `assets/style.css`, `assets/app.js`: ortak görünüm ve etkileşimler.
- `api/contact.php`: sunucu doğrulaması ve e-posta gönderimi.

CSS/JS adresleri içerik hash'i taşır. Kaynak değişikliklerinden sonra build çalıştırın. Sayfa kaydırma animasyonları yalnızca dikey konumu değiştirir; beyazlama/opacity efekti kullanılmaz. Hareket azaltma tercihi desteklenir. Yazı tipleri yüklenemezse sistem fontu kullanılır.

## URL, ürün menüsü ve marka açılışı

Kamuya açık sayfa adresleri `/urunler`, `/ic-mekan-led-ekran` ve `/urun-grand-air-ic-mekan` biçimindedir. Diskteki HTML dosyaları korunur. Üretimde Apache `mod_rewrite` ve `.htaccess` kuralları uzantısız adresleri bu dosyalardan sunar; eski `.html` adresleri sorgu parametreleri korunarak 301 ile yönlenir. `index.html` köke yönlenir. Site içi bağlantılar, canonical adresleri ve sitemap uzantısızdır. Nginx-only kurulumlarda aynı yönlendirme ve `try_files $uri $uri.html =404` davranışı ayrıca sunucu yapılandırmasında tanımlanmalıdır. `npm run dev` PHP router ile eşdeğer adresleri destekler.

Masaüstü Ürünler menüsü 31 modeli üç grupta listeler. Fareyle üzerine gelmek veya klavyeyle odaklamak sağdaki görsel/açıklama/incele bağlantısını günceller. Ürün fotoğrafı olmayan zemin kabininde başka bir ürünün görselini göstermek yerine kaynak fotoğrafının bulunmadığı belirtilir. Mobilde doğrudan ürün bağlantıları kullanılır. Beş çözüm sayfasında gerçek üretici fotoğrafları ve ilgili ürünler; katalogda görselli koleksiyon kartları yer alır.

Ana sayfanın özgün Canvas/CSS açılışı yaklaşık 2,2 saniye sürer; sekme oturumunda bir kez gösterilir. Atla düğmesi, Escape ve Tab ile kapanır. Hareket azaltma tercihinde veya JavaScript yokken gösterilmez; video indirme veya yükleme beklemez. Referans Xeron sayfası bu ortamdan HTTP 403 döndürdüğü için tamamı incelenemedi; kullanıcının paylaştığı menü ekran görüntüsü tasarım referansı olarak kullanıldı.

`python3 scripts/navigation-visual-check.py` geliştirme sunucusu üzerinde temiz adresleri, eski adres yönlendirmelerini, altı sayfanın ürün görsellerini, 31 ürünün önizlemesini ve marka açılışının erişilebilir kapanma davranışını doğrular.

## Etkileşimli deneyimler

Ana sayfada `#urun-deneyimi` scroll anlatımı ve üretici fotoğrafına oturan dört etkileşimli nokta; `#ekran-planlayici` altında boyutlandırıcı ve piksel aralığı simülasyonu bulunur. Grand Air ürün detaylarında da kabin noktaları kullanılabilir. Yeni hero, harici video indirmeyen özgün bir Canvas ışık animasyonudur; mimari fotoğrafa geçiş ve durdurma/başlatma düğmeleri vardır. Sekme gizliyken veya alan görünmüyorken animasyon çalışmaz; hareket azaltma tercihinde duraklar.

Katalogdaki ve ürün detaylarındaki karşılaştırma düğmeleri en fazla üç ürün seçer. Modal tabloda yalnızca farklar gösterilebilir; seçimlerin tamamı iletişim formuna aktarılabilir. Sekme oturumunda sessionStorage sadece halka açık ürün kimliklerini tutar. Modül/kabin boyutlandırıcı, üretici föylerinden türetilen 42 gerçek seçenek üzerinden ölçüyü birim katlarına yuvarlar, toplam adedi ve çözünürlüğü hesaplar. Varyantlar ayrı seçilir; dinamik piksel serisinde fiziksel piksel çözünürlüğü kullanılır. Çelişkili zemin föyü bu hesapta kullanılmaz. Çerçeve, taşıyıcı ve kurulum payları hesap dışıdır. Hesaplanan ölçü ve ürün, teklif formuna taşınır.

Piksel simülasyonu açıklayıcı bir modeldir; gerçek göz/kamera testi veya kesin izleme mesafesi hesabı değildir. Tam ekran uygulama galerisi dört **konsept** sahnesi içerir ve müşteri referansı olarak sunulmaz. Klavye okları, Escape, kapatma düğmesi ve mobil kaydırma kullanılabilir. Sayfalar arası geçişler destekleyen tarayıcılarda yerel View Transitions API ile çalışır; ürün görseli karttan detay sayfasına taşınır. Bağlantı tıklamaları engellenmez; eski tarayıcılar normal gezinmeye devam eder. Hareket azaltma tercihi desteklenir.

`assets/leddisplay-logo-navy.png`, kullanıcının paylaştığı lacivert ve şeffaf zeminli logodur. Üst menü, footer ve karşılama ekranında kullanılır. `npm run test:experience` hesaplamaları ve sekiz deneyimin tarayıcı davranışlarını kontrol eder; gerçek e-posta göndermez.

## İletişim formu

Form, ziyaretçiyi sayfadan çıkarmadan `POST /api/contact.php` üzerinden bilgileri ve tüm seçilen ürünleri **info@leddisplay.com.tr** adresine yollar. Gönderici sabit olarak `LEDDISPLAY <info@leddisplay.com.tr>`; Reply-To doğrulanmış ziyaretçi e-postasıdır. SMTP şifresi veya diğer kimlik bilgileri repoya eklenmez. Özel SMTP ayar dosyası varsa PHPMailer 7.1.1 ile şifreli ve kimlik doğrulamalı SMTP kullanılır. Ayar dosyası henüz oluşturulmadıysa mevcut PHP `mail()` aktarımı korunur. SMTP yapılandırılmışken bağlantı/şifre/sertifika hatasında yerel `mail()` aktarımına geri dönülmez.

- GET isteği, yalnızca form gönderimi gerektiğinde oturum bağlı doğrulama anahtarı üretir.
- Zorunlu alanlar, e-posta, uzunluklar ve ürünler sunucuda doğrulanır. Alıcı adresi ziyaretçi tarafından değiştirilemez.
- CSRF/origin kontrolü, honeypot ve oturumlar arasında IP başına 15 dakikada 5 deneme sınırı vardır.
- Sayaç, sistem geçici dizininde yalnızca zaman damgaları tutar; dosya adı IP'nin hash'ini içerir. Mesaj içeriği veya açık IP bu sayaçta tutulmaz.
- Oturumda başarılı talebin kimliği ve içeriğinin hash'i saklanır. Aynı talebin tekrar denenmesi ikinci e-posta oluşturmaz; farklı içerikle aynı kimlik kullanımı reddedilir.
- Yalnızca seçilen posta servisi mesajı kabul edince başarı ekranı ve talep numarası gösterilir. SMTP veya `mail()` kabulü, alıcı posta kutusuna son teslim veya okunma teyidi değildir.
- Gönderim/bağlantı hatasında form bilgileri korunur. Arayüz bir başarı bildirimi taklit etmez. İsteğe bağlı özet indirme e-posta göndermez.
- E-posta içeriği uygulama veri tabanına yazılmaz; posta kuyruğu ve alıcı posta kutusunda işlenir. Gizlilik ve çerez sayfaları bu davranışı açıklar. İşletmeye özgü KVKK/unvan/başvuru bilgileri ayrıca tamamlanmalıdır.

Telefon: **0549 900 91 77** (`tel:+905499009177`). WhatsApp: `https://wa.me/905499009177`. WhatsApp kısayolları yalnızca mesaj taslağı açar, otomatik mesaj göndermez.

## Plesk üzerinden Pull → Deploy

1. Natro'da kök alan adı (`@`) A kaydı `194.36.87.191` olmalı. `www` için kök alan adına CNAME veya aynı IP'ye A kaydı kullanın. DNS ve canlı sunucu bu bulut oturumundan doğrulanmış değildir.
2. Plesk'te belge kökü `httpdocs`, Git deposu `https://github.com/Mchdozr/leddisplay.git`, dal `main`, dağıtım modu **Manual** olmalı. **Pull**, ardından **Deploy** kullanın. Sunucuda npm/build gerekmez; üretilmiş dosyalar repodadır.
3. Hosting/PHP ayarlarında **PHP 8.1 veya üzeri** etkin olmalı; PHP-FPM uygundur. PHP dosyaları kaynak metin olarak sunulmamalıdır. `api/contact.php` ve `data/products.json` dahil tüm dosyaları dağıtın.
4. Natro posta kutusu için aşağıdaki SMTP yapılandırmasını uygulayın; PHP OpenSSL etkin olmalı. Ayar dosyası yokken eski yerel `mail()` yolu kullanılır ve Plesk posta servisini gerektirir. Oturum ve sistem geçici dizinleri PHP kullanıcısı tarafından yazılabilir olmalı. `open_basedir` özel SMTP dosyasını ve bu dizinleri okumaya izin vermeli.
5. `info@leddisplay.com.tr` Plesk'te barınıyorsa posta kutusunun varlığını doğrulayın. Natro/başka sağlayıcıda barınıyorsa Plesk yerel alan adı teslimatının mesajı yanlış yerel kutuya yönlendirmediğini ve MX yönlendirmesini kontrol edin. SPF/DKIM ve giden SMTP erişimi, gerçek teslim edilebilirliği etkiler.
6. Let's Encrypt ile kök alan adı ve `www` için HTTPS etkinleştirin; tercih edilen alan adına yönlendirin. Üretimde form oturum çerezi HTTPS gerektirir.
7. Dağıtımdan sonra gerçek formu doldurun; info posta kutusu ve spam klasöründe mesajı ve talep numarasını kontrol edin. Başarı ekranı posta kuyruğu kabulünü gösterir. İleti gelmezse aynı talep numarasıyla Plesk posta kuyruğu/günlüklerini inceleyin. Gönderim hatası olursa arayüz bilgileri korur.

Özel GitHub deposu için Plesk'in SSH anahtarını salt okunur deploy key olarak ekleyebilirsiniz. Github hesap şifresini kod veya sohbet içine yazmayın. Apache `.htaccess`, geliştirici belgelerini ve `data/`, `scripts/` dizinlerini dış erişime kapatır. Nginx-only kurulumlarda eşdeğer erişim kurallarını sunucu ayarlarında uygulayın. `data/products.json` kamuya açık katalog verisidir ve backend tarafından dosya sisteminden okunur; gizli bilgi içermez.

Bulut ortamından leddisplay.com.tr erişimi ağ politikası nedeniyle engellendiği için canlı Plesk PHP/mail ayarları veya gerçek posta kutusuna teslimat doğrulanmadı. Kod testleri ile canlı teslimat kontrolü ayrı işlemlerdir.

## Natro SMTP — Plesk üzerinde özel yapılandırma

Hesap sahibi Outlook ayarlarını `mail.kurumsaleposta.com`, giden SMTP `465`, gelen IMAP `993` olarak bildirdi. Örnek dosya giden posta için **465 / örtük SSL/TLS** kullanır. Form posta okumadığı için 993 kullanılmaz. Natro destek sayfası bu çalışma ortamından HTTP 403 döndürüyor; gerçek hesapla SMTP bağlantısı henüz doğrulanmadı.

1. Plesk **Dosyalar** bölümünde `httpdocs` klasörünün bir üstüne, alan adının ana dizinine geçin. `httpdocs` ile aynı seviyede **`leddisplay-mail.php`** dosyası oluşturun.
2. [Örnek dosyanın](deployment/leddisplay-mail.example.php) içeriğini buraya aktarın. `host`, `port`, `encryption` değerlerini Natro panelindeki bilgilere göre doldurun. `tls` STARTTLS, `ssl` bağlantı başında TLS demektir. Örnek dosya hesap sahibinin verdiği `mail.kurumsaleposta.com`, `465`, `ssl` değerleriyle hazırdır.
3. `username` değeri `info@leddisplay.com.tr` kalır. `password` alanına bu posta kutusunun şifresini **yalnızca Plesk dosya düzenleyicisinde** yazın. PHP tek tırnaklı metin içinde `'` ve `\` karakterlerini sırasıyla `\'` ve `\\` olarak kaçırın. Dosyayı GitHub’a veya sohbet mesajına koymayın; erişim izni hosting kullanıcısına özel `0600` olmalı.
4. `api/mail-transport.php` ve `api/vendor/phpmailer/` dahil yeni kodu **Pull → Deploy** ile alın. SMTP ayar dosyası Git dağıtım alanının dışında olduğu için sonraki dağıtımlarda korunur. PHP OpenSSL ve Plesk’ten ilgili SMTP portuna giden erişim gerekir.
5. Gerçek formdan bir talep gönderip Natro webmail’de aynı talep numarasıyla iletiyi kontrol edin. SMTP sunucusunun kabulü son teslim teyidi değildir. Hata olursa şifreyi veya mesaj içeriğini paylaşmadan sunucu günlüklerini inceleyin.

Özel dosya varsa geçersiz/eksik ayarda veya SMTP hatasında form 503 döndürür ve ziyaretçinin bilgilerini korur. Şifre veya SMTP hata ayrıntıları istemciye/günlüklere yazılmaz. TLS sertifika ve sunucu adı doğrulaması kapatılmaz. Yerel testler gerçek posta göndermez: `python3 scripts/smtp-check.py` TLS üzerinden kimlik doğrulama, UTF-8 içerik, sabit alıcı/gönderici, Reply-To, reddedilen şifre/ileti/sertifika ve geçersiz ayarda geri dönüş olmamasını kontrol eder.

## Paket

```sh
npm run package
```

`/workspace/leddisplay-plesk.zip` üretilir. Pakette HTML, varlıklar/PDF'ler, `api/contact.php`, backend için katalog JSON'u ve erişim kuralları bulunur. Geliştirici araçları eklenmez. Dosya Yöneticisi ile `httpdocs` içine açılabilir. Var olan canlı dosyaları önce yedekleyin. Paket üretimi canlı dağıtım yapmaz.

## Doğrulama

```sh
npm test
npm run test:contact
# Site 3000 portunda çalışırken:
npm run test:browser
```

- Statik kontrol: 48 sayfa, yerel bağlantılar, bölüm hedefleri, PDF/ürün eşleşmeleri ve SHA-256 kaynak özetleri.
- PHP entegrasyonu: gerçek PHP uç noktası ve yalnızca yerel dosyaya kaydeden test posta aktarımı. Gerçek e-posta göndermez. Doğrulama, yanlış CSRF/origin, başlık enjeksiyonu, iki ürün içeriği, sabit alıcı/Reply-To, tekrar gönderim, mail hatası/yeniden deneme ve oturumlar arası hız sınırı kontrol edilir.
- Aynı entegrasyon testi gerçek PHP + Chromium ile form hatasında bilgi korumayı, sayfadan çıkmadan başarı ekranını, eşleşen talep numarasını ve mobil düzeni doğrular. Python Playwright ve Chromium gerekir.
- Tarayıcı testleri: tüm sayfalar, kategorili menü ve URL filtreleri, çoklu ürün/özet indirme, çözüm seçici, hareket azaltma, 31 ürünün sabit galerisi ve görsel büyütme.

## Ürün kaynakları ve görseller

`data/products.json`, iki kullanıcı spec arşivindeki 31 benzersiz föyden aktarılmış 26 modül ve 5 kabin/ürün ailesini içerir. İki birebir kopya SHA-256 ile ayıklanmıştır. Grand Air aileleri çoklu boyut/piksel seçeneklerini ayrı varyant tablosunda gösterir. Kaynak eşlemesi ve çelişkiler `DATA_SOURCES.md` içindedir. Özellikle P0.93 dinamik/fiziksel aralık, P3.91 zemin IP çelişkisi ve Grand Air dış mekân parlaklık seçenekleri üretici teyidi gerektirir.

Ürün fotoğrafları PDF'lerden çıkarılmıştır. Ana sayfadaki mimari/mağaza/sahne görselleri temsilî üretilmiş konseptlerdir; gerçekleşmiş müşteri projeleri değildir. Firma geçmişi, sertifika, garanti, müşteri logoları ve referans projeler doğrulanmadan eklenmemelidir.

## Akıcı kaydırma hareketi

Ekranın altındaki kartlar kullanıcı görmeden önce 18 px aşağıda hazırlanır; görünür alana yaklaşırken tek seferlik, 760 ms yumuşak çıkış eğrisiyle yerine gelir. Görünür kartlar başlangıçta oynatılmaz. Hareket, hover efektinin `transform` özelliği yerine bağımsız CSS `translate` özelliğini kullanır; opaklık değişmez. Kısa kademelendirme en fazla 75 ms'dir. Geçici compositor ipucu animasyon bitince kaldırılır ve son kare sabitlendikten sonra animasyon temizlenir. Hareket azaltma tercihinde bekleyen ve çalışan hareketler tamamen temizlenir. Site 3000 portunda çalışırken `npm run test:motion` masaüstü/mobil ana sayfa ve katalogda kareler arasında ters sıçrama, opaklık, bitiş konumu ve temizlik davranışını doğrular; gerçek cihaz performansı ayrıca tarayıcı ve donanıma bağlıdır.
