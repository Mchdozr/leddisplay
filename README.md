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

## İletişim formu

Form, ziyaretçiyi sayfadan çıkarmadan `POST /api/contact.php` üzerinden bilgileri ve tüm seçilen ürünleri **info@leddisplay.com.tr** adresine yollar. Gönderici sabit olarak `LEDDISPLAY <info@leddisplay.com.tr>`; Reply-To doğrulanmış ziyaretçi e-postasıdır. SMTP şifresi veya diğer kimlik bilgileri repoya eklenmez. PHP `mail()` ile Plesk'in yerel posta aktarımı kullanılır.

- GET isteği, yalnızca form gönderimi gerektiğinde oturum bağlı doğrulama anahtarı üretir.
- Zorunlu alanlar, e-posta, uzunluklar ve ürünler sunucuda doğrulanır. Alıcı adresi ziyaretçi tarafından değiştirilemez.
- CSRF/origin kontrolü, honeypot ve oturumlar arasında IP başına 15 dakikada 5 deneme sınırı vardır.
- Sayaç, sistem geçici dizininde yalnızca zaman damgaları tutar; dosya adı IP'nin hash'ini içerir. Mesaj içeriği veya açık IP bu sayaçta tutulmaz.
- Oturumda başarılı talebin kimliği ve içeriğinin hash'i saklanır. Aynı talebin tekrar denenmesi ikinci e-posta oluşturmaz; farklı içerikle aynı kimlik kullanımı reddedilir.
- Sadece yerel posta servisi mesajı kabul edince başarı ekranı ve talep numarası gösterilir. `mail()` kabulü, alıcı posta kutusuna son teslim veya okunma teyidi değildir.
- Gönderim/bağlantı hatasında form bilgileri korunur. Arayüz bir başarı bildirimi taklit etmez. İsteğe bağlı özet indirme e-posta göndermez.
- E-posta içeriği uygulama veri tabanına yazılmaz; posta kuyruğu ve alıcı posta kutusunda işlenir. Gizlilik ve çerez sayfaları bu davranışı açıklar. İşletmeye özgü KVKK/unvan/başvuru bilgileri ayrıca tamamlanmalıdır.

Telefon: **0549 900 91 77** (`tel:+905499009177`). WhatsApp: `https://wa.me/905499009177`. WhatsApp kısayolları yalnızca mesaj taslağı açar, otomatik mesaj göndermez.

## Plesk üzerinden Pull → Deploy

1. Natro'da kök alan adı (`@`) A kaydı `194.36.87.191` olmalı. `www` için kök alan adına CNAME veya aynı IP'ye A kaydı kullanın. DNS ve canlı sunucu bu bulut oturumundan doğrulanmış değildir.
2. Plesk'te belge kökü `httpdocs`, Git deposu `https://github.com/Mchdozr/leddisplay.git`, dal `main`, dağıtım modu **Manual** olmalı. **Pull**, ardından **Deploy** kullanın. Sunucuda npm/build gerekmez; üretilmiş dosyalar repodadır.
3. Hosting/PHP ayarlarında **PHP 8.1 veya üzeri** etkin olmalı; PHP-FPM uygundur. PHP dosyaları kaynak metin olarak sunulmamalıdır. `api/contact.php` ve `data/products.json` dahil tüm dosyaları dağıtın.
4. Plesk'in yerel mail servisi (ör. Postfix/sendmail) çalışmalı ve PHP `mail()` devre dışı bırakılmamış olmalı. Oturum ve sistem geçici dizinleri PHP kullanıcısı tarafından yazılabilir olmalı. `open_basedir` bu dizinlere izin vermeli.
5. `info@leddisplay.com.tr` Plesk'te barınıyorsa posta kutusunun varlığını doğrulayın. Natro/başka sağlayıcıda barınıyorsa Plesk yerel alan adı teslimatının mesajı yanlış yerel kutuya yönlendirmediğini ve MX yönlendirmesini kontrol edin. SPF/DKIM ve giden SMTP erişimi, gerçek teslim edilebilirliği etkiler.
6. Let's Encrypt ile kök alan adı ve `www` için HTTPS etkinleştirin; tercih edilen alan adına yönlendirin. Üretimde form oturum çerezi HTTPS gerektirir.
7. Dağıtımdan sonra gerçek formu doldurun; info posta kutusu ve spam klasöründe mesajı ve talep numarasını kontrol edin. Başarı ekranı posta kuyruğu kabulünü gösterir. İleti gelmezse aynı talep numarasıyla Plesk posta kuyruğu/günlüklerini inceleyin. Gönderim hatası olursa arayüz bilgileri korur.

Özel GitHub deposu için Plesk'in SSH anahtarını salt okunur deploy key olarak ekleyebilirsiniz. Github hesap şifresini kod veya sohbet içine yazmayın. Apache `.htaccess`, geliştirici belgelerini ve `data/`, `scripts/` dizinlerini dış erişime kapatır. Nginx-only kurulumlarda eşdeğer erişim kurallarını sunucu ayarlarında uygulayın. `data/products.json` kamuya açık katalog verisidir ve backend tarafından dosya sisteminden okunur; gizli bilgi içermez.

Bulut ortamından leddisplay.com.tr erişimi ağ politikası nedeniyle engellendiği için canlı Plesk PHP/mail ayarları veya gerçek posta kutusuna teslimat doğrulanmadı. Kod testleri ile canlı teslimat kontrolü ayrı işlemlerdir.

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
