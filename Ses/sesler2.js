// Kule katları efektleri (sentez, node): Teneke (çarpma + sekmeler + yuvarlanma), Homurtu (iri düşman sesi duydu)
const fs = require("fs"), path = require("path");
const OUT = process.argv[2] || "."; const SR = 48000;
let seed = 11; const rnd = () => { seed = (seed * 1664525 + 1013904223) >>> 0; return seed / 4294967296; };
const gauss = () => { let u = 0; for (let i = 0; i < 6; i++) u += rnd(); return (u - 3) / Math.sqrt(0.5); };
function biquadBP(x, f0, q) { // RBJ bant geçiren
  const w = 2 * Math.PI * f0 / SR, al = Math.sin(w) / (2 * q), c = Math.cos(w);
  const b0 = al, b2 = -al, a0 = 1 + al, a1 = -2 * c, a2 = 1 - al; const y = new Float64Array(x.length);
  let x1 = 0, x2 = 0, y1 = 0, y2 = 0;
  for (let i = 0; i < x.length; i++) { const v = (b0 * x[i] + b2 * x2 - a1 * y1 - a2 * y2) / a0; x2 = x1; x1 = x[i]; y2 = y1; y1 = v; y[i] = v; }
  return y;
}
function write(name, x) {
  let m = 0; for (const v of x) m = Math.max(m, Math.abs(v)); const g = 0.85 / (m + 1e-9);
  const n = x.length, buf = Buffer.alloc(44 + n * 2);
  buf.write("RIFF", 0); buf.writeUInt32LE(36 + n * 2, 4); buf.write("WAVE", 8); buf.write("fmt ", 12); buf.writeUInt32LE(16, 16);
  buf.writeUInt16LE(1, 20); buf.writeUInt16LE(1, 22); buf.writeUInt32LE(SR, 24); buf.writeUInt32LE(SR * 2, 28); buf.writeUInt16LE(2, 32); buf.writeUInt16LE(16, 34);
  buf.write("data", 36); buf.writeUInt32LE(n * 2, 40);
  for (let i = 0; i < n; i++) buf.writeInt16LE(Math.round(Math.max(-1, Math.min(1, x[i] * g)) * 32767), 44 + i * 2);
  fs.writeFileSync(path.join(OUT, name + ".wav"), buf); console.log("YAZILDI", name, (n / SR).toFixed(2));
}
// ---- teneke ----
{
  const n = Math.round(1.6 * SR), k = new Float64Array(n);
  const KISMI = [[1.0, 22], [1.58, 30], [2.31, 38], [3.07, 45], [4.43, 60], [5.9, 75]];
  for (const [t0, a, f0] of [[0, 1, 1240], [0.21, 0.55, 1310], [0.36, 0.3, 1180], [0.45, 0.18, 1270]]) {
    const i0 = Math.round(t0 * SR); const nz = new Float64Array(n - i0).map(() => gauss()); const nzf = biquadBP(nz, 6000, 0.7);
    const fazlar = KISMI.map(() => rnd() * 6);
    for (let i = 0; i < n - i0; i++) {
      const tt = i / SR; let s = 0;
      KISMI.forEach(([r, d], j) => { s += Math.sin(2 * Math.PI * f0 * r * tt + fazlar[j]) * Math.exp(-tt * d) / Math.pow(j + 1, 0.7); });
      s += 0.6 * nzf[i] * Math.exp(-tt * 90);
      k[i0 + i] += a * s * Math.min(1, tt * 4000);
    }
  }
  const tcs = Array.from({ length: 26 }, () => 0.5 + rnd() * 0.75).sort();
  for (const tc of tcs) { const i0 = Math.round(tc * SR), f = 1700 + rnd() * 900, m = Math.min(n - i0, Math.round(0.04 * SR));
    for (let i = 0; i < m; i++) { const tt = i / SR; k[i0 + i] += 0.08 * Math.exp(-(tc - 0.5) * 2.2) * Math.sin(2 * Math.PI * f * tt) * Math.exp(-tt * 160); } }
  const g = biquadBP(new Float64Array(n).map(() => gauss()), 800, 0.8);
  for (let i = 0; i < n; i++) { const t = i / SR; if (t > 0.5 && t < 1.25) k[i] += 0.05 * g[i] * Math.exp(-(t - 0.5) * 3); }
  write("Teneke", k);
}
// ---- homurtu ----
{
  const n = Math.round(1.5 * SR), saw = new Float64Array(n); let ph = 0;
  for (let i = 0; i < n; i++) { const t = i / SR; const f = 72 - 14 * t / 1.5 + 3 * Math.sin(2 * Math.PI * 5.5 * t); ph += f / SR; saw[i] = 2 * (ph % 1) - 1; }
  const a = biquadBP(saw, 180, 0.6), b = biquadBP(saw, 550, 2.5), nz = biquadBP(new Float64Array(n).map(() => gauss()), 700, 0.6);
  const h = new Float64Array(n);
  for (let i = 0; i < n; i++) { const t = i / SR; const env = Math.min(1, t * 6) * Math.exp(-Math.max(0, t - 0.9) * 5);
    h[i] = (a[i] + 0.5 * b[i] + 0.35 * nz[i] * (0.5 + 0.5 * Math.sin(2 * Math.PI * 3 * t) ** 2)) * env; }
  write("Homurtu", h);
}
