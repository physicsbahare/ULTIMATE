#!/bin/sh
cd /home/bahareh/ULTIMATE || exit 1
nohup setsid /home/bahareh/miniforge3/envs/phd/bin/python -u /home/bahareh/ULTIMATE/data/TNG50_SKIRT_DR1_ml_expansion/download_expansion.py >> /home/bahareh/ULTIMATE/data/TNG50_SKIRT_DR1_ml_expansion/download.log 2>&1 < /dev/null &
printf 'Expansion wrapper PID %s; authoritative PID in data/TNG50_SKIRT_DR1_ml_expansion/download.pid\n' "$!"
