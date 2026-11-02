# Sisli — karanlık ambiyans müziği + sokak lambası vızıltısı (tamamen sentez, lisans derdi yok)
# Katmanlar: alçak drone (D1/D2, akordu kaçık), yavaş minör pad, rüzgâr, seyrek akordu bozuk müzik kutusu, uzak gümbürtü,
# evrişimli yankı. Sonuç döngülü (son 6 sn başa harmanlanır).
# kullanım: python muzik.py <çıktı_klasörü>
import numpy as np, wave, sys, os
OUT = sys.argv[1] if len(sys.argv) > 1 else "."
SR = 48000; DUR = 150.0; XF = 6.0
rng = np.random.default_rng(13)
N = int((DUR + XF) * SR); t = np.arange(N) / SR

def smooth_noise(n, rate_hz, seed):
    r = np.random.default_rng(seed); k = max(4, int(n / SR * rate_hz) + 4)
    pts = r.random(k); x = np.linspace(0, k - 3, n)
    i = np.floor(x).astype(int); f = x - i; f = f * f * (3 - 2 * f)
    return pts[i] * (1 - f) + pts[i + 1] * f

def saw_dark(freq, n, tilt=1.6, harm=18, phase=0.0):
    s = np.zeros(n); tt = np.arange(n) / SR
    for h in range(1, harm + 1):
        if freq * h > 6000: break
        s += np.sin(2 * np.pi * freq * h * tt + phase * h) / h ** tilt
    return s

def fft_filter(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    g = np.exp(-0.5 * (np.maximum(0, lo - f) / (lo * 0.25 + 1)) ** 2) * np.exp(-0.5 * (np.maximum(0, f - hi) / (hi * 0.25 + 1)) ** 2)
    return np.fft.irfft(X * g, len(x))

L = np.zeros(N); R = np.zeros(N)
# 1) alçak drone
lfo = 0.6 + 0.4 * smooth_noise(N, 0.05, 1)
L += 0.30 * lfo * (np.sin(2 * np.pi * 36.71 * t) + 0.6 * np.sin(2 * np.pi * 73.42 * t))
R += 0.30 * lfo * (np.sin(2 * np.pi * 36.80 * t) + 0.6 * np.sin(2 * np.pi * 73.62 * t))
dr = saw_dark(73.42, N, 2.2, 10)
L += 0.05 * dr * smooth_noise(N, 0.04, 2); R += 0.05 * np.roll(dr, 900) * smooth_noise(N, 0.04, 3)
# 2) pad: Dm → Bb/D → Gm/D → Dm(b6), her biri 25 sn, yumuşak geçiş
chords = [[146.83, 174.61, 220.00], [116.54, 146.83, 174.61], [98.00, 146.83, 233.08], [146.83, 174.61, 233.08]]
seg = 25.0
for ci in range(int((DUR + XF) / seg) + 2):
    notes = chords[ci % len(chords)]
    c0 = (ci - 0.5) * seg
    env = np.clip(1 - np.abs((t - (c0 + seg / 2)) / (seg * 0.75)), 0, 1) ** 1.5
    if env.max() == 0: continue
    for k, f in enumerate(notes):
        det = 1 + rng.uniform(-0.003, 0.003)
        v = saw_dark(f * det, N, 1.9, 14, rng.uniform(0, 6)) * env * (0.5 + 0.5 * smooth_noise(N, 0.08, 100 + ci * 7 + k))
        p = 0.5 + 0.35 * (k - 1)
        L += 0.06 * v * (1 - p); R += 0.06 * v * p
# 3) rüzgâr
wn = rng.standard_normal(N)
gust = smooth_noise(N, 0.07, 5) ** 2
w1 = fft_filter(wn, 180, 700) * (0.25 + 0.75 * gust)
w2 = fft_filter(rng.standard_normal(N), 900, 1300) * smooth_noise(N, 0.05, 6) ** 3
w3 = fft_filter(rng.standard_normal(N), 520, 610) * smooth_noise(N, 0.06, 7) ** 4   # ıslık
wind = 0.9 * w1 / (np.abs(w1).max() + 1e-9) + 0.5 * w2 / (np.abs(w2).max() + 1e-9) + 0.35 * w3 / (np.abs(w3).max() + 1e-9)
pan = smooth_noise(N, 0.03, 8)
L += 0.10 * wind * (1 - pan); R += 0.10 * wind * pan
# 4) müzik kutusu notaları (akordu hafif bozuk, inharmonik)
scale = [293.66, 349.23, 440.00, 466.16, 523.25, 587.33, 659.26]
tm = 4.0
while tm < DUR + XF - 4:
    f = scale[rng.integers(len(scale))] * 2 ** (rng.uniform(-25, 25) / 1200)
    i0 = int(tm * SR); n = int(4.0 * SR); tt = np.arange(n) / SR
    tone = (np.sin(2 * np.pi * f * tt) + 0.35 * np.sin(2 * np.pi * f * 2.76 * tt) * np.exp(-tt * 3) + 0.15 * np.sin(2 * np.pi * f * 5.4 * tt) * np.exp(-tt * 6))
    tone *= np.exp(-tt * 1.1) * np.minimum(1, tt * 400) * rng.uniform(0.5, 1.0)
    p = rng.uniform(0.2, 0.8); e = min(N, i0 + n) - i0
    L[i0:i0 + e] += 0.07 * tone[:e] * (1 - p); R[i0:i0 + e] += 0.07 * tone[:e] * p
    if rng.random() < 0.3:   # bazen ikinci nota (aralık: küçük ikili — tedirgin)
        tm2 = tm + rng.uniform(0.25, 0.6); i1 = int(tm2 * SR); f2 = f * 2 ** (1 / 12); e2 = min(N, i1 + n) - i1
        tone2 = np.sin(2 * np.pi * f2 * tt) * np.exp(-tt * 1.3) * np.minimum(1, tt * 400) * 0.6
        L[i1:i1 + e2] += 0.06 * tone2[:e2] * p; R[i1:i1 + e2] += 0.06 * tone2[:e2] * (1 - p)
    tm += rng.uniform(5.5, 12.0)
# 5) uzak gümbürtü
for tb in np.arange(18.0, DUR, 37.0):
    i0 = int(tb * SR); n = int(5 * SR); tt = np.arange(n) / SR
    fr = 55 * np.exp(-tt * 0.5) + 28
    b = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-tt * 1.2) * np.minimum(1, tt * 30)
    nz = fft_filter(rng.standard_normal(n), 40, 220) * np.exp(-tt * 2.0); nz /= np.abs(nz).max() + 1e-9
    e = min(N, i0 + n) - i0
    L[i0:i0 + e] += 0.22 * (b + 0.4 * nz)[:e]; R[i0:i0 + e] += 0.20 * (b + 0.4 * nz)[:e]
# 6) yankı (koyu, 5 sn kuyruk)
def reverb(x, seed):
    n = int(5.0 * SR); tt = np.arange(n) / SR
    ir = np.random.default_rng(seed).standard_normal(n) * np.exp(-tt * 1.35)
    ir = fft_filter(ir, 60, 2500); ir[:int(0.03 * SR)] = 0; ir /= np.sqrt((ir ** 2).sum())
    m = 1 << int(np.ceil(np.log2(len(x) + n)))
    y = np.fft.irfft(np.fft.rfft(x, m) * np.fft.rfft(ir, m), m)[:len(x) + n]
    y[:n] += y[len(x):len(x) + n]   # kuyruğu başa sar (döngü)
    return y[:len(x)]
WL, WR = reverb(L, 21), reverb(R, 22)
L = 0.62 * L + 0.55 * WL / (np.abs(WL).max() + 1e-9) * np.abs(L).max()
R = 0.62 * R + 0.55 * WR / (np.abs(WR).max() + 1e-9) * np.abs(R).max()
# döngü: son XF saniyeyi başa harmanla
nx = int(XF * SR); n0 = int(DUR * SR)
fade = np.linspace(0, 1, nx)
for ch in (L, R):
    ch[:nx] = ch[:nx] * fade + ch[n0:n0 + nx] * (1 - fade)
L, R = L[:n0], R[:n0]
pk = max(np.abs(L).max(), np.abs(R).max()); L *= 0.7 / pk; R *= 0.7 / pk
def write(path, chans):
    data = np.stack(chans, -1) if len(chans) > 1 else chans[0][:, None]
    data = (np.clip(data, -1, 1) * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(data.shape[1]); w.setsampwidth(2); w.setframerate(SR); w.writeframes(data.tobytes())
    print("YAZILDI", path, round(len(data) / SR, 1), "sn")
os.makedirs(OUT, exist_ok=True)
write(os.path.join(OUT, "Sisli_Ambiyans.wav"), [L, R])

# --- sokak lambası vızıltısı (mono, 3 sn döngü: 50 Hz'in tam katı) ---
n = 3 * SR; tt = np.arange(n) / SR
hum = 0.5 * np.sin(2 * np.pi * 50 * tt) + 0.35 * np.sin(2 * np.pi * 100 * tt) + 0.2 * np.sin(2 * np.pi * 150 * tt)
buzz = np.sign(np.sin(2 * np.pi * 100 * tt)) * 0.15
buzz = fft_filter(buzz, 400, 3000)
flick = 1 - 0.25 * (np.random.default_rng(9).random(n) < 0.0004).astype(float)
flick = np.convolve(flick, np.ones(400) / 400, mode="same")
lamp = (hum + 1.5 * buzz) * flick
lamp *= 0.6 / np.abs(lamp).max()
write(os.path.join(OUT, "Lamba_Vizilti.wav"), [lamp])
