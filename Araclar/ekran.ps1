# Kullanim: powershell -File ekran.ps1 <surecAdi> <cikti.png>
param($proc, $out)
$code = @'
using System; using System.Runtime.InteropServices; using System.Drawing;
public class E {
  [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  public struct RECT { public int L,T,R,B; }
  public static void Shot(IntPtr h, string path){ SetProcessDPIAware(); RECT r; GetWindowRect(h, out r); var b=new Bitmap(r.R-r.L, r.B-r.T); using(var g=Graphics.FromImage(b)){ g.CopyFromScreen(r.L,r.T,0,0,b.Size);} b.Save(path); }
}
'@
Add-Type -TypeDefinition $code -ReferencedAssemblies System.Drawing
$p = Get-Process $proc | Where-Object { $_.MainWindowHandle -ne 0 } | Select-Object -First 1
[E]::Shot($p.MainWindowHandle, $out); "ok $($p.MainWindowTitle)"
