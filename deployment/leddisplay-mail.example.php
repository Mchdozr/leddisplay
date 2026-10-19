<?php
// Create leddisplay-mail.php in the domain directory ONE LEVEL ABOVE httpdocs.
// Fill values using Natro's account-specific SMTP settings; this example is not active.
// Restrict permissions to the hosting user (0600). Never put this file in Git/httpdocs.
return [
    'host' => 'NATRO_PANELINDEKI_SMTP_SUNUCUSU',
    'port' => 587, // Use the port specified by Natro.
    'encryption' => 'tls', // tls = STARTTLS (usually 587); ssl = implicit TLS (usually 465).
    'username' => 'info@leddisplay.com.tr',
    'password' => 'SADECE_SUNUCUDA_EPOSTA_SIFRESINI_GIRIN',
];
