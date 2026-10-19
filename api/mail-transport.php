<?php
declare(strict_types=1);

/** Use authenticated SMTP when configured; retain the existing transport until setup. */
function sendContactMail(string $subject, string $body, array $headers): bool {
    // Outside httpdocs: never committed, deployed or downloadable from the website.
    $configPath = dirname(__DIR__, 2) . '/leddisplay-mail.php';
    if (!is_file($configPath)) {
        return function_exists('mail') && @mail('info@leddisplay.com.tr', $subject, $body, $headers, '-finfo@leddisplay.com.tr');
    }
    $config = require $configPath;
    if (!is_array($config)) {
        throw new RuntimeException('SMTP configuration is invalid.');
    }
    $host = $config['host'] ?? '';
    $username = $config['username'] ?? '';
    $password = $config['password'] ?? '';
    $security = $config['encryption'] ?? '';
    $port = $config['port'] ?? 0;
    if (!is_string($host) || !preg_match('/^[a-z0-9.-]+$/iD', $host) ||
        $username !== 'info@leddisplay.com.tr' || !is_string($password) || $password === '' ||
        !in_array($security, ['tls', 'ssl'], true) || !is_int($port) || $port < 1 || $port > 65535) {
        throw new RuntimeException('SMTP configuration is incomplete.');
    }
    if (!extension_loaded('openssl')) {
        throw new RuntimeException('SMTP requires OpenSSL.');
    }
    require_once __DIR__ . '/vendor/phpmailer/Exception.php';
    require_once __DIR__ . '/vendor/phpmailer/SMTP.php';
    require_once __DIR__ . '/vendor/phpmailer/PHPMailer.php';
    $mailer = new PHPMailer\PHPMailer\PHPMailer(true);
    $mailer->isSMTP();
    $mailer->Host = $host;
    $mailer->Port = $port;
    $mailer->SMTPSecure = $security;
    $mailer->SMTPAuth = true;
    $mailer->Username = $username;
    $mailer->Password = $password;
    $mailer->Timeout = 8;
    $mailer->Timelimit = 12;
    $mailer->SMTPDebug = 0;
    // Keep certificate and hostname verification enabled. Never log credentials or content.
    $mailer->SMTPOptions = ['ssl' => ['verify_peer' => true, 'verify_peer_name' => true, 'allow_self_signed' => false]];
    $mailer->CharSet = 'UTF-8';
    $mailer->Encoding = 'base64';
    $mailer->setFrom('info@leddisplay.com.tr', 'LEDDISPLAY');
    $mailer->addAddress('info@leddisplay.com.tr');
    $mailer->addReplyTo($headers['Reply-To']);
    $mailer->MessageID = $headers['Message-ID'];
    $mailer->Subject = $subject;
    $mailer->Body = $body;
    return $mailer->send();
}
