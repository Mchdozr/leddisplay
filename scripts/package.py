"""Build a deployment archive containing only publicly served site files."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

root = Path(__file__).resolve().parents[1]
target = root.parent / 'leddisplay-plesk.zip'
files = sorted(root.glob('*.html')) + sorted((root / 'assets').rglob('*'))
files += [root / '.htaccess', root / 'robots.txt', root / 'sitemap.xml']
with ZipFile(target, 'w', ZIP_DEFLATED) as archive:
    for path in files:
        if path.is_file():
            archive.write(path, path.relative_to(root))
with ZipFile(target) as archive:
    assert archive.testzip() is None
    assert 'index.html' in archive.namelist()
    assert '.htaccess' in archive.namelist()
    assert len([name for name in archive.namelist() if name.endswith('.pdf')]) == 31
print(f'Validated Plesk archive: {target} ({target.stat().st_size:,} bytes)')
