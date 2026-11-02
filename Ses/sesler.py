# Sisli efekt sesleri (sentez): Anahtar, Gicirti, Yakalandi, FenerTik
import numpy as np, wave, sys, os
OUT = sys.argv[1] if len(sys.argv) > 1 else "."
SR = 48000; rng = np.random.default_rng(5)
def write(name, x):
    x = x / (np.abs(x).max() + 1e-9) * 0.8
    d = (np.clip(x, -1, 1) * 32767).astype(np.int16)
    with wave.open(os.path.join(OUT, name + ".wav"), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(d.tobytes())
    print("YAZILDI", name, round(len(x) / SR, 2))
def bp(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    return np.fft.irfft(X * ((f > lo) & (f < hi)), len(x))
# anahtar: iki metalik vuruş (inharmonik kısmi tonlar) + kısa şıngırtı
n = int(1.4 * SR); t = np.arange(n) / SR; k = np.zeros(n)
for t0, f0, a in ((0.0, 1850, 1.0), (0.11, 2380, 0.7)):
    i = int(t0 * SR); tt = t[: n - i]
    s = sum(np.sin(2 * np.pi * f0 * r * tt) * np.exp(-tt * d) / (j + 1) for j, (r, d) in enumerate(((1, 6), (2.41, 9), (3.87, 14), (5.2, 20))))
    k[i:] += a * s * np.minimum(1, tt * 2000)
k += 0.15 * bp(rng.standard_normal(n), 3000, 9000) * np.exp(-t * 30)
write("Anahtar", k)
# gıcırtı: perdesi titreyen testere dişi, bant geçiren + sürtünme gürültüsü
n = int(2.2 * SR); t = np.arange(n) / SR
f = 190 + 70 * np.sin(2 * np.pi * 0.7 * t) + 25 * np.sin(2 * np.pi * 7.3 * t) + 40 * rng.standard_normal(n).cumsum() / np.sqrt(n) * 3
ph = 2 * np.pi * np.cumsum(f) / SR
saw = 2 * ((ph / (2 * np.pi)) % 1) - 1
g = bp(saw, 400, 3200) * (0.4 + 0.6 * np.abs(np.sin(2 * np.pi * 2.1 * t)) ** 2)
g += 0.3 * bp(rng.standard_normal(n), 800, 2500) * np.abs(np.sin(2 * np.pi * 3.3 * t))
env = np.minimum(1, t * 8) * np.exp(-np.maximum(0, t - 1.7) * 6)
write("Gicirti", g * env)
# yakalandı: alçak darbe + yükselen gürültü + uyumsuz yaylı akoru
n = int(2.6 * SR); t = np.arange(n) / SR
hit = np.sin(2 * np.pi * (48 * np.exp(-t * 1.5) + 30) * t) * np.exp(-t * 2.5)
swell = bp(rng.standard_normal(n), 120, 1600) * np.minimum(1, t / 1.2) * np.exp(-np.maximum(0, t - 1.4) * 3)
cl = sum(np.sin(2 * np.pi * fr * t + rng.uniform(0, 6)) for fr in (155.6, 164.8, 233.1, 246.9)) * np.minimum(1, t / 0.6) * np.exp(-np.maximum(0, t - 1.6) * 2.5)
write("Yakalandi", 1.0 * hit + 0.5 * swell / (np.abs(swell).max() + 1e-9) + 0.25 * cl / 4)
# fener tık
n = int(0.12 * SR); t = np.arange(n) / SR
write("FenerTik", bp(rng.standard_normal(n), 1500, 7000) * np.exp(-t * 90) + 0.4 * np.sin(2 * np.pi * 900 * t) * np.exp(-t * 120))
