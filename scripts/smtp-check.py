"""Exercise real PHPMailer over verified TLS against a local SMTP server only."""
import base64
from email import policy
from email.parser import BytesParser
import json
from pathlib import Path
import shutil
import socketserver
import ssl
import subprocess
import tempfile
import threading

ROOT = Path(__file__).resolve().parents[1]
PHP = shutil.which('php') or str(ROOT.parent / '.tools/leddisplay-php/php')

class SMTP(socketserver.StreamRequestHandler):
    def handle(self):
        def send(line):
            self.wfile.write(line.encode() + b'\r\n'); self.wfile.flush()
        send('220 localhost test SMTP')
        encrypted = False
        authenticated = False
        while line := self.rfile.readline():
            command = line.decode().strip()
            verb = command.split(' ', 1)[0].upper()
            if verb == 'EHLO':
                send('250-localhost')
                if not encrypted: send('250-STARTTLS')
                send('250 AUTH LOGIN')
            elif verb == 'STARTTLS':
                send('220 Ready for TLS')
                try:
                    self.connection = self.server.tls.wrap_socket(self.connection, server_side=True)
                except ssl.SSLError:
                    return  # Expected when the client rejects our untrusted test certificate.
                self.rfile = self.connection.makefile('rb'); self.wfile = self.connection.makefile('wb')
                encrypted = True
            elif verb == 'AUTH':
                assert encrypted, 'Credentials must never be sent before TLS'
                send('334 ' + base64.b64encode(b'Username:').decode())
                username = base64.b64decode(self.rfile.readline().strip()).decode()
                send('334 ' + base64.b64encode(b'Password:').decode())
                password = base64.b64decode(self.rfile.readline().strip()).decode()
                authenticated = username == 'info@leddisplay.com.tr' and password == 'local-test-only' and not self.server.reject_auth
                send('235 Authenticated' if authenticated else '535 Authentication failed')
            elif verb in ('MAIL', 'RCPT'):
                assert encrypted and authenticated
                assert 'info@leddisplay.com.tr' in command
                send('250 OK')
            elif verb == 'DATA':
                assert authenticated
                send('354 End with dot')
                lines = []
                while (part := self.rfile.readline()) != b'.\r\n':
                    if not part: return
                    lines.append(part[1:] if part.startswith(b'..') else part)
                if self.server.reject_data: send('550 Message rejected')
                else:
                    self.server.messages.append(b''.join(lines)); send('250 Queued')
            elif verb == 'QUIT':
                send('221 Bye'); return
            elif verb == 'RSET': send('250 Reset')
            else: send('500 Unsupported')

with tempfile.TemporaryDirectory(prefix='leddisplay-smtp-') as temp:
    folder = Path(temp); web = folder / 'httpdocs'; web.mkdir()
    shutil.copytree(ROOT / 'api', web / 'api')
    cert = folder / 'cert.pem'; key = folder / 'key.pem'
    subprocess.run(['openssl', 'req', '-x509', '-newkey', 'rsa:2048', '-nodes', '-days', '1',
                    '-subj', '/CN=localhost', '-addext', 'subjectAltName=DNS:localhost',
                    '-keyout', str(key), '-out', str(cert)], check=True, capture_output=True)
    tls = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER); tls.load_cert_chain(cert, key)
    with socketserver.ThreadingTCPServer(('127.0.0.1', 0), SMTP) as server:
        server.daemon_threads = True; server.tls = tls; server.messages = []
        server.reject_auth = False; server.reject_data = False
        thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        config = folder / 'leddisplay-mail.php'
        config.write_text("<?php return ['host'=>'localhost','port'=>" + str(server.server_address[1]) +
                          ",'encryption'=>'tls','username'=>'info@leddisplay.com.tr','password'=>'local-test-only'];")
        runner = web / 'run.php'
        runner.write_text("<?php require __DIR__.'/api/mail-transport.php'; try { $ok=sendContactMail('Türkçe SMTP testi', 'İki ürün ve proje açıklaması.', ['Reply-To'=>'visitor@example.com','Message-ID'=>'<ld-test@leddisplay.com.tr>']); echo json_encode(['ok'=>$ok]); } catch (Throwable $e) { echo json_encode(['ok'=>false]); }")
        def run(trusted=True):
            args = [PHP, '-n', '-d', 'display_errors=stderr', '-d', 'sendmail_path=/bin/false']
            if trusted: args += ['-d', f'openssl.cafile={cert}']
            result = subprocess.run(args + [str(runner)], check=True, capture_output=True, text=True, timeout=25)
            assert 'local-test-only' not in result.stdout + result.stderr
            return json.loads(result.stdout)['ok']
        assert run() is True
        assert len(server.messages) == 1
        message = BytesParser(policy=policy.default).parsebytes(server.messages[0])
        assert str(message['Subject']) == 'Türkçe SMTP testi'
        assert str(message['Reply-To']) == 'visitor@example.com'
        assert message['To'] == 'info@leddisplay.com.tr'
        assert 'İki ürün' in message.get_content()
        server.reject_auth = True
        assert run() is False
        server.reject_auth = False; server.reject_data = True
        assert run() is False
        server.reject_data = False
        assert run(trusted=False) is False, 'Untrusted TLS certificates must fail'
        config.write_text("<?php return ['host'=>'localhost'];")
        assert run() is False, 'Invalid SMTP config must not fall back to local mail'
        assert len(server.messages) == 1
        server.shutdown(); thread.join()
print('SMTP: verified STARTTLS, authenticated fixed sender/recipient, UTF-8, Reply-To, rejected credentials/message/certificate, invalid config and no local fallback passed. No external email sent.')
