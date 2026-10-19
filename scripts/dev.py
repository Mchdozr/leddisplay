"""Run the complete development site with PHP, including the contact endpoint."""
from pathlib import Path
import os
import shutil

root=Path(__file__).resolve().parents[1]
php=shutil.which('php') or str(root.parent/'.tools/leddisplay-php/php')
if not Path(php).exists():
    raise SystemExit('PHP 8.1+ is required. Install PHP CLI, then run npm run dev again.')
os.execv(php,[php,'-S','0.0.0.0:3000','-t',str(root),str(root/'scripts/router.php')])
