# Additional TNG50-SKIRT DR1 acquisition

Acquisition only. No scientific analysis or extraction is started. Existing data and prior analysis outputs are preserved.

## Selection

The saved official Baes24 DR1 catalogue contains 1,154 distinct galaxies. Exclude294866 and recognized local archive IDs before selection. The metadata provide stellar/gas/dark-matter masses, SFR and stellar half-mass radius, but no morphological classification. Select one seeded random galaxy in each of five stellar-mass quantiles × five activity strata: zero SFR, then four positive-sSFR quartiles. Seed20261026; exact selected metadata are in selected_galaxies.csv and selection_manifest.json. This is a deliberately balanced feasibility sample, not a volume-representative sample or a verified disk-only sample. Radius is retained as size metadata, not treated as a morphology label.

Only the user-specified TNG50-1/snapshot99 DR1 skirt_atlas.tar.gz API route is used. The API redirects to the official data-eu.tng-project.org HTTPS host. The API-key header is stripped on a hostname change; signed redirect URLs, query strings and response bodies are never logged or saved. The actual API key is read internally from the owner-only600 ~/.tng_api_key; no key is passed on the command line, in environment variables, or in generated files. Redirects containing the literal saved credential are blocked.

## Verification and storage

Preflight performs bounded archive range requests to check actual gzip bytes, byte-range support, authentication/access and compressed sizes. A signed-data-host403 is distinguished from an authenticated-API401/403 and retried via the original API route. selection_manifest.json records expected full sizes and ETag/Last-Modified validators, never signed URLs. preflight.json records safe response metadata only. No batch starts before successful preflight.

Downloads are sequential and use .tar.gz.part until full expected byte length and gzip CRC/tar payload validation pass. All regular tar payloads are read, gzip is drained through EOF, and a local SHA256 is computed. No tar members are extracted. Verified archives are atomically renamed to .tar.gz. The state records byte length, mtime_ns, SHA256 and archive-member counts. Restart skips unchanged verified files, verifies untracked completed archives, and resumes partial transfers with Range/If-Range. A server refusing valid range continuation cannot cause accidental appending of a full response. HTTP/connectivity and stream interruptions retry with backoff. Integrity failures remain recorded and existing bytes are retained for inspection; they are not silently accepted or deleted.

The hard compressed-data cap is65GiB across new archives/partials; the free-space floor is100GiB plus256MiB safety headroom. These are checked during transfer. Preflight also checks the total expected size and free-space requirement. Other processes can independently consume disk space, so the downloader rechecks continuously and pauses if necessary. Known old archives outside this output directory are excluded from the new-data cap and never modified.

## Launch, monitor, stop, restart

Use the existing environment; install nothing:

```sh
cd /home/bahareh/ULTIMATE
/home/bahareh/miniforge3/envs/phd/bin/python data/TNG50_SKIRT_DR1_extra/download_dr1.py --preflight
sh data/TNG50_SKIRT_DR1_extra/start_download.sh
```

The launcher uses nohup and setsid, redirects stdin from /dev/null, and appends to tng50_dr1_download.log. The downloader itself writes its authoritative process ID to tng50_dr1_download.pid only after obtaining an exclusive lock, preventing concurrent batches.

```sh
tail -f /home/bahareh/ULTIMATE/tng50_dr1_download.log
ps -p "$(cat /home/bahareh/ULTIMATE/tng50_dr1_download.pid)" -o pid,etime,stat,args
/home/bahareh/miniforge3/envs/phd/bin/python -m json.tool /home/bahareh/ULTIMATE/data/TNG50_SKIRT_DR1_extra/download_state.json
df -h /home/bahareh/ULTIMATE
du -sh /home/bahareh/ULTIMATE/data/TNG50_SKIRT_DR1_extra
```

Stop gracefully after checking that the PID above still belongs to this downloader:

```sh
kill -TERM "$(cat /home/bahareh/ULTIMATE/tng50_dr1_download.pid)"
```

Restart/resume with the same launcher. There is no need to rerun sample selection. A duplicate launch exits without starting another batch. A stale PID file after exit is harmless; check ps and the state rather than assuming a PID file means a live process.

Six offline tests cover interrupted-transfer continuation, verified skipping, malformed gzip/tar rejection, disk/budget guards, credential-safe redirects, HTTP retry/auth failure and preservation of mismatched existing files. Run with the existing phd interpreter: `python test_downloader.py`. Tests use a synthetic credential and temporary miniature archives, not the saved real key or science downloads.
