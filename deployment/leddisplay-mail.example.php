<?php
// Create leddisplay-mail.php in the domain directory ONE LEVEL ABOVE httpdocs.
// Fill values using Natro's account-specific SMTP settings; this example is not active.
// Restrict permissions to the hosting user (0600). Never put this file in Git/httpdocs.
return [
    'host' => 'mail.kurumsaleposta.com',
    'port' => 465, // Natro outgoing SMTP port supplied by the account owner.
    'encryption' => 'ssl', // Implicit TLS on port 465; IMAP 993 is not used by the form.
    'username' => 'info@leddisplay.com.tr',
    'password' => 'SADECE_SUNUCUDA_EPOSTA_SIFRESINI_GIRIN',
];
