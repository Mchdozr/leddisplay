"""Render the original LEDDISPLAY light-reveal film, using the supplied logo silhouette.

Offline authoring only: Python, Pillow, NumPy and ffmpeg. No production dependencies.
Run: python3 scripts/render-brand-film.py [--preview]
"""
from pathlib import Path
import argparse
import subprocess
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/video'
FPS, DURATION = 30, 5.4
LOGO = Image.open(ROOT / 'assets/leddisplay-logo-navy.png').convert('RGBA')
LOGO = LOGO.crop(LOGO.getbbox())
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'


def ease(value):
    value = np.clip(value, 0, 1)
    return value * value * (3 - 2 * value)


class Film:
    def __init__(self, portrait):
        self.portrait = portrait
        self.w, self.h = (1080, 1920) if portrait else (1920, 1080)
        self.logo_w = round(self.w * .70)
        self.logo_h = round(self.logo_w * LOGO.height / LOGO.width)
        self.x = (self.w - self.logo_w) // 2
        self.y = round(self.h * (.44 if portrait else .40))
        alpha = LOGO.getchannel('A').resize((self.logo_w, self.logo_h), Image.Resampling.LANCZOS)
        self.alpha = np.asarray(alpha, dtype=np.float32) / 255
        self.edge = np.asarray(alpha.filter(ImageFilter.MaxFilter(3)), dtype=np.float32) / 255 - np.asarray(alpha.filter(ImageFilter.MinFilter(3)), dtype=np.float32) / 255
        self.lx = np.linspace(0, 1, self.logo_w)[None, :]
        self.ly = np.linspace(0, 1, self.logo_h)[:, None]
        self.gx, self.gy = np.meshgrid(np.linspace(0, 1, self.w // 4), np.linspace(0, 1, self.h // 4))
        self.rng = np.random.default_rng(2031)
        self.particles = self.rng.random((115, 4))

    def label(self, image, text, y, opacity, size, tracking, color):
        if opacity <= 0:
            return
        layer = Image.new('RGBA', image.size)
        draw = ImageDraw.Draw(layer)
        font = ImageFont.truetype(FONT, size)
        width = sum(draw.textlength(c, font=font) for c in text) + tracking * (len(text) - 1)
        x = (self.w - width) / 2
        for char in text:
            draw.text((x, y), char, font=font, fill=(*color, round(opacity * 255)))
            x += draw.textlength(char, font=font) + tracking
        image.alpha_composite(layer)

    def frame(self, t):
        w, h = self.w, self.h
        gx, gy = self.gx, self.gy
        # Slowly shifting pools of light; the edges remain nearly black.
        teal = np.exp(-((gx - (.38 + .08 * math.sin(t * .45))) ** 2 / .16 + (gy - .45) ** 2 / .16))
        orange = np.exp(-((gx - .84) ** 2 / .09 + (gy - .68) ** 2 / .018))
        vignette = np.clip(1 - ((gx - .5) ** 2 + (gy - .5) ** 2), 0, 1)
        rgb = np.stack([5 + teal * 6 + orange * 23, 12 + teal * 20 + orange * 8, 24 + teal * 31 + orange * 2], axis=-1)
        rgb *= vignette[..., None]
        image = Image.fromarray(np.uint8(np.clip(rgb, 0, 255))).resize((w, h), Image.Resampling.BILINEAR).convert('RGBA')
        glow = Image.new('RGBA', (w, h))
        draw = ImageDraw.Draw(glow)
        horizon = h * .71
        # A luminous LED plane recedes toward the wordmark.
        for row in range(1, 24):
            depth = row / 24
            y = horizon + depth ** 1.9 * h * .31
            step = 17 + depth * 42
            for x in np.arange(-step, w + step, step):
                pulse = .55 + .45 * math.sin(x * .007 + t * 1.3 + row * .45)
                a = round((8 + depth * 27) * pulse * float(ease(t / .8)))
                radius = .6 + depth * .8
                draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(78, 147, 174, a))
        # Restrained light trails, converging into the logo rather than crossing its face.
        trails = Image.new('RGBA', (w, h))
        td = ImageDraw.Draw(trails)
        intensity = math.sin(min(1, t / 4.6) * math.pi) * .72 + .12
        for index in range(3):
            points = []
            for x in range(-10, w + 11, 8):
                u = x / w
                y = horizon + math.sin(u * 4.5 + index * .24 - t * .25) * h * .055 + index * 6
                points.append((x, y))
            td.line(points, fill=(*( (239, 107, 45) if index == 0 else (45, 146, 180)), round(100 * intensity)), width=2)
        image.alpha_composite(trails.filter(ImageFilter.GaussianBlur(17)))
        image.alpha_composite(trails)
        image.alpha_composite(glow)
        # Fine particles move inward and fade as the identity resolves.
        particles = Image.new('RGBA', (w, h)); pd = ImageDraw.Draw(particles)
        settle = float(ease((t - .25) / 2.7))
        for px, py, depth, seed in self.particles:
            x = (px * (1 - settle * .28) + .5 * settle * .28) * w
            y = (py * (1 - settle * .2) + .46 * settle * .2) * h - t * (4 + depth * 5)
            a = round((.35 + .65 * math.sin(seed * 20 + t) ** 2) * (20 + depth * 65) * (1 - .7 * settle))
            r = .6 + depth * .8
            pd.ellipse((x-r, y-r, x+r, y+r), fill=(125, 184, 212, a))
        image.alpha_composite(particles)

        # Mark first, then a left-to-right letter reveal using the exact supplied silhouette.
        scan = -.12 + 1.28 * float(ease((t - .65) / 2.2))
        reveal = ease((scan - self.lx) / .045)
        mark = ease((t - .22) / .8)
        reveal = np.where(self.lx < .19, mark, reveal)
        fill = ease((t - 1.6 - self.lx * .85) / .65)
        opacity = self.alpha * reveal * (.15 + .85 * fill)
        edge_opacity = self.edge * reveal * (1 - fill) * .8
        sweep = np.exp(-((self.lx - scan) / .018) ** 2) * self.alpha * .95 if t < 3 else np.zeros_like(self.alpha)
        final_alpha = np.clip(opacity + edge_opacity + sweep, 0, 1)
        color = np.zeros((self.logo_h, self.logo_w, 4), dtype=np.uint8)
        shade = 1 - self.ly * .12
        for channel, value in enumerate([235, 245, 252]):
            color[:, :, channel] = np.uint8(np.clip(value * shade + sweep * (20 if channel != 2 else 3), 0, 255))
        color[:, :, 3] = np.uint8(final_alpha * 255)
        face = Image.fromarray(color)
        # Soft ambient bloom and a shallow bevel keep the wordmark dimensional.
        halo = Image.new('RGBA', (w, h)); halo.alpha_composite(face, (self.x, self.y))
        bloom = halo.filter(ImageFilter.GaussianBlur(12))
        bloom.putalpha(bloom.getchannel('A').point(lambda value: int(value * .24)))
        image.alpha_composite(bloom)
        shadow = Image.new('RGBA', face.size, (16, 45, 64, 0))
        shadow.putalpha(face.getchannel('A').point(lambda value: int(value * .55)))
        image.alpha_composite(shadow, (self.x + 2, self.y + 4))
        image.alpha_composite(face, (self.x, self.y))
        # A faint reflected silhouette on the LED plane.
        reflection = face.transpose(Image.Transpose.FLIP_TOP_BOTTOM).resize((self.logo_w, round(self.logo_h * .55)))
        fade = np.linspace(.1, 0, reflection.height)[:, None]
        reflection.putalpha(Image.fromarray(np.uint8(np.asarray(reflection.getchannel('A')) * fade)))
        image.alpha_composite(reflection, (self.x, self.y + self.logo_h + 35))
        label_y = self.y + self.logo_h + (86 if self.portrait else 72)
        label_fade = float(ease((t - 2.8) / .75))
        self.label(image, 'GÖRÜNTÜNÜN YENİ RİTMİ.', label_y, label_fade, 20 if self.portrait else 17, 5, (168, 192, 208))
        self.label(image, 'LED EKRAN TEKNOLOJİLERİ', round(h * .20), float(ease((t - .25) / .7)) * .7, 16 if self.portrait else 13, 4, (170, 189, 207))
        accent = Image.new('RGBA', (w, h)); ad = ImageDraw.Draw(accent)
        length = 45 * float(ease((t - 2.9) / .7))
        ad.line((w/2-length, label_y+52, w/2+length, label_y+52), fill=(239, 107, 45, round(label_fade*190)), width=2)
        image.alpha_composite(accent)
        return image.convert('RGB')

    def render(self):
        name = 'leddisplay-brand-intro-v3' + ('-portrait' if self.portrait else '')
        mp4 = OUT / f'{name}.mp4'
        command = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-f', 'rawvideo', '-vcodec', 'rawvideo', '-s', f'{self.w}x{self.h}', '-pix_fmt', 'rgb24', '-r', str(FPS), '-i', '-', '-an', '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(mp4)]
        process = subprocess.Popen(command, stdin=subprocess.PIPE)
        for index in range(round(FPS * DURATION)):
            process.stdin.write(self.frame(index / FPS).tobytes())
            if index % 45 == 0:
                print(f'{name}: frame {index}/{round(FPS * DURATION)}', flush=True)
        process.stdin.close()
        if process.wait():
            raise RuntimeError('H.264 encoding failed')
        self.frame(0).save(OUT / f'{name}-poster.jpg', quality=91)
        subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', str(mp4), '-an', '-c:v', 'libvpx-vp9', '-b:v', '0', '-crf', '32', '-cpu-used', '4', str(OUT / f'{name}.webm')], check=True)
        print(f'Finished {name}', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--preview', action='store_true')
    args = parser.parse_args()
    OUT.mkdir(exist_ok=True)
    for portrait in (False, True):
        film = Film(portrait)
        if args.preview:
            film.frame(3.8).save(f'/tmp/leddisplay-film-{portrait}.jpg', quality=92)
        else:
            film.render()
