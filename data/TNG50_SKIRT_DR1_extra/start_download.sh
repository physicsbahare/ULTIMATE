#!/bin/sh
# Credential is read internally from ~/.tng_api_key, never from argv/env/URL.
cd /home/bahareh/ULTIMATE || exit 1
nohup setsid /home/bahareh/miniforge3/envs/phd/bin/python -u /home/bahareh/ULTIMATE/data/TNG50_SKIRT_DR1_extra/download_dr1.py >> /home/bahareh/ULTIMATE/tng50_dr1_download.log 2>&1 < /dev/null &
printf 'Launched background wrapper PID %s; authoritative PID is written by the downloader.\n' "$!"
