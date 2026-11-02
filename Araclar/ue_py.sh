#!/bin/bash
# Başsız UE Python, düşük öncelik: ue_py.sh <script.py> [NullRHI=1]   (-1 ile hemen çıkarsa 3 kez yeniden dener)
S="$1"; RHI="${2:-1}"; EXTRA=""; [ "$RHI" = "1" ] && EXTRA="-NullRHI"
rm -f "$S.log" 2>/dev/null
for i in 1 2 3; do
  R=$(powershell -c "\$p = Start-Process 'C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe' -ArgumentList '\"C:/Users/Onur/Sisli/Unreal/Sisli.uproject\" -run=pythonscript -script=\"$S\" -unattended -nop4 -nosplash $EXTRA -abslog=\"$S.log\"' -PassThru -WindowStyle Hidden; try { \$p.PriorityClass = 'BelowNormal' } catch {}; \$p.WaitForExit(); \$p.ExitCode")
  R=$(echo "$R" | tr -d '\r' | tail -1)
  if [ "$R" != "-1" ]; then echo "cikis $R"; exit 0; fi
  sleep 15
done
echo "cikis $R (3 deneme)"
