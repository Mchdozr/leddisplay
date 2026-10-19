<?php
declare(strict_types=1);

// PHP 8.1+: authenticated SMTP when configured, otherwise the existing local transport.
// Credentials are read only from a private server file outside httpdocs.
ini_set('display_errors', '0');
ini_set('session.use_strict_mode', '1');
date_default_timezone_set('Europe/Istanbul');
header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store, private');
header('X-Content-Type-Options: nosniff');
header('X-Robots-Tag: noindex, nofollow');

function reply(int $status, array $body): never {
    http_response_code($status);
    echo json_encode($body, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
    exit;
}

$method = $_SERVER['REQUEST_METHOD'] ?? '';
if (!in_array($method, ['GET', 'POST'], true)) {
    header('Allow: GET, POST');
    reply(405, ['ok' => false, 'message' => 'Bu işlem desteklenmiyor.']);
}
$host = strtolower((string) parse_url('http://' . ($_SERVER['HTTP_HOST'] ?? ''), PHP_URL_HOST));
$origin = $_SERVER['HTTP_ORIGIN'] ?? '';
if ($origin !== '' && strtolower((string) parse_url($origin, PHP_URL_HOST)) !== $host) {
    reply(403, ['ok' => false, 'message' => 'İsteğiniz doğrulanamadı. Lütfen iletişim sayfasından yeniden deneyin.']);
}
$local = in_array($host, ['localhost', '127.0.0.1', '[::1]'], true);
session_name('leddisplay_contact');
session_set_cookie_params(['lifetime' => 0, 'path' => '/', 'secure' => !$local, 'httponly' => true, 'samesite' => 'Lax']);
if (!session_start()) {
    reply(503, ['ok' => false, 'message' => 'İletişim servisi şu anda kullanılamıyor. Lütfen daha sonra deneyin.']);
}
if ($method === 'GET') {
    if (empty($_SESSION['csrf']) || ($_SESSION['csrf_expires'] ?? 0) < time()) {
        $_SESSION['csrf'] = bin2hex(random_bytes(32));
        $_SESSION['csrf_expires'] = time() + 3600;
    }
    reply(200, ['ok' => true, 'csrf' => $_SESSION['csrf']]);
}
if ((int) ($_SERVER['CONTENT_LENGTH'] ?? 0) > 32768) {
    reply(413, ['ok' => false, 'message' => 'Mesajınız çok uzun. Lütfen kısaltarak yeniden deneyin.']);
}
$raw = file_get_contents('php://input', false, null, 0, 32769);
if ($raw === false || strlen($raw) > 32768) {
    reply(413, ['ok' => false, 'message' => 'Mesajınız işlenemedi. Lütfen kısaltarak yeniden deneyin.']);
}
$input = json_decode($raw, true);
if (!is_array($input)) {
    reply(400, ['ok' => false, 'message' => 'Form verileri okunamadı. Lütfen sayfayı yenileyip deneyin.']);
}
$csrf = $input['csrf'] ?? '';
if (!is_string($csrf) || empty($_SESSION['csrf']) || ($_SESSION['csrf_expires'] ?? 0) < time() || !hash_equals($_SESSION['csrf'], $csrf)) {
    reply(403, ['ok' => false, 'message' => 'Form oturumunuz yenilenmeli. Bilgileriniz korunuyor; lütfen tekrar gönderin.']);
}
function field(array $input, string $key, int $min, int $max, bool $oneLine = true): string {
    $value = $input[$key] ?? '';
    if (!is_string($value) || !preg_match('//u', $value)) {
        reply(422, ['ok' => false, 'message' => 'Lütfen form alanlarını geçerli bilgilerle doldurun.']);
    }
    $value = trim($value);
    $length = preg_match_all('/./us', $value);
    if ($length < $min || $length > $max || ($oneLine && preg_match('/[\r\n\x00-\x1F\x7F]/u', $value)) || str_contains($value, "\0")) {
        reply(422, ['ok' => false, 'message' => 'Lütfen zorunlu alanları ve alan uzunluklarını kontrol edin.']);
    }
    return $value;
}
$name = field($input, 'name', 2, 100);
$company = field($input, 'company', 0, 150);
$email = field($input, 'email', 3, 150);
$phone = field($input, 'phone', 0, 30);
$solution = field($input, 'solution', 1, 150);
$message = field($input, 'message', 15, 5000, false);
$honeypot = field($input, 'website', 0, 200);
if ($honeypot !== '' || !filter_var($email, FILTER_VALIDATE_EMAIL)) {
    reply(422, ['ok' => false, 'message' => 'Lütfen form bilgilerinizi kontrol edin.']);
}
$products = $input['products'] ?? [];
if (!is_array($products) || !array_is_list($products) || count($products) > 31) {
    reply(422, ['ok' => false, 'message' => 'Ürün seçimi geçerli değil.']);
}
$catalog = json_decode((string) file_get_contents(dirname(__DIR__) . '/data/products.json'), true);
if (!is_array($catalog)) {
    reply(503, ['ok' => false, 'message' => 'Ürün bilgileri yüklenemedi. Lütfen daha sonra deneyin.']);
}
$allowed = array_column($catalog, 'title');
foreach ($products as $product) {
    if (!is_string($product) || !in_array($product, $allowed, true)) {
        reply(422, ['ok' => false, 'message' => 'Seçtiğiniz ürünler doğrulanamadı.']);
    }
}
$products = array_values(array_unique($products));
$requestId = $input['requestId'] ?? '';
if (!is_string($requestId) || !preg_match('/^[a-f0-9-]{16,64}$/i', $requestId)) {
    reply(422, ['ok' => false, 'message' => 'Gönderim bilgisi doğrulanamadı. Lütfen sayfayı yenileyin.']);
}
$fingerprint = hash('sha256', json_encode([$name, $company, $email, $phone, $solution, $message, $products]));
foreach (($_SESSION['sent'] ?? []) as $key => $record) {
    if ($record['time'] < time() - 3600) unset($_SESSION['sent'][$key]);
}
if (isset($_SESSION['sent'][$requestId])) {
    $record = $_SESSION['sent'][$requestId];
    if (!hash_equals($record['fingerprint'], $fingerprint)) {
        reply(409, ['ok' => false, 'message' => 'Bu gönderim numarası daha önce kullanıldı. Lütfen sayfayı yenileyin.']);
    }
    reply(200, ['ok' => true, 'reference' => $record['reference']]);
}

// Rate limit across sessions. Store timestamps only, never message contents or raw IPs.
$ratePath = sys_get_temp_dir() . '/leddisplay-contact-' . hash('sha256', dirname(__DIR__) . '|' . ($_SERVER['REMOTE_ADDR'] ?? 'unknown')) . '.json';
$rateFile = @fopen($ratePath, 'c+');
if ($rateFile === false || !flock($rateFile, LOCK_EX)) {
    reply(503, ['ok' => false, 'message' => 'Gönderim servisi meşgul. Lütfen daha sonra deneyin.']);
}
@chmod($ratePath, 0600);
$times = json_decode(stream_get_contents($rateFile) ?: '[]', true);
$times = array_values(array_filter(is_array($times) ? $times : [], fn($time) => is_int($time) && $time > time() - 900));
if (count($times) >= 5) {
    flock($rateFile, LOCK_UN);
    fclose($rateFile);
    header('Retry-After: 900');
    reply(429, ['ok' => false, 'message' => 'Kısa sürede çok fazla talep gönderildi. Lütfen 15 dakika sonra tekrar deneyin veya bizi arayın.']);
}
$times[] = time();
ftruncate($rateFile, 0);
rewind($rateFile);
$encoded = json_encode($times);
$written = fwrite($rateFile, $encoded);
fflush($rateFile);
flock($rateFile, LOCK_UN);
fclose($rateFile);
if ($written !== strlen($encoded)) {
    reply(503, ['ok' => false, 'message' => 'Gönderim servisi şu anda kullanılamıyor. Lütfen daha sonra deneyin.']);
}

$reference = 'LD-' . date('ymd') . '-' . strtoupper(bin2hex(random_bytes(4)));
$subject = 'LEDDISPLAY | ' . $reference . ' | Yeni talep';
$body = "LEDDISPLAY WEB SİTESİ — YENİ TALEP\n\n" .
    "Talep numarası: $reference\nTarih: " . date('d.m.Y H:i:s T') . "\n\n" .
    "Ad Soyad: $name\nFirma: " . ($company ?: 'Belirtilmedi') . "\nE-posta: $email\nTelefon: " . ($phone ?: 'Belirtilmedi') . "\nTalep türü: $solution\n\n" .
    "Seçilen ürünler:\n" . ($products ? implode("\n", $products) : 'Henüz ürün seçilmedi') . "\n\nProje açıklaması:\n$message\n";
$headers = [
    'From' => 'LEDDISPLAY <info@leddisplay.com.tr>',
    'Reply-To' => $email,
    'MIME-Version' => '1.0',
    'Content-Type' => 'text/plain; charset=UTF-8',
    'Content-Transfer-Encoding' => '8bit',
    'Message-ID' => '<' . strtolower($reference) . '@leddisplay.com.tr>',
];
$accepted = false;
try {
    require_once __DIR__ . '/mail-transport.php';
    $accepted = sendContactMail($subject, $body, $headers);
} catch (Throwable $error) {
    error_log('LEDDISPLAY contact: mail transport unavailable.');
}
if (!$accepted) {
    reply(503, ['ok' => false, 'message' => 'Mesajınız şu anda gönderilemedi. Bilgileriniz korunuyor; lütfen tekrar deneyin veya 0549 900 91 77 numarasından bize ulaşın.']);
}
$_SESSION['sent'][$requestId] = ['time' => time(), 'fingerprint' => $fingerprint, 'reference' => $reference];
reply(200, ['ok' => true, 'reference' => $reference]);
