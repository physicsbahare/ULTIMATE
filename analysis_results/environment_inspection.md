# Python/environment inspection

Existing environments found:

| Environment | Python | Availability checked | Decision |
| --- | --- | --- | --- |
| `/home/bahareh/miniforge3/envs/phd` | 3.12.15 | Astropy, NumPy, SciPy, Matplotlib, pandas, Jupyter, nbformat, nbclient, photutils, SEP | Reused for all new analysis; registered kernel `phd` |
| `/home/bahareh/environments/astro` | 3.9.13 | Astropy, NumPy, SciPy, Matplotlib and Jupyter import specs present; nbclient absent | Existing astronomy venv; registered `astro-nthu`; no changes |
| `HAWKI_GRAAL/.venv` | 3.11.17 | Astropy/NumPy present, SciPy/Matplotlib/Jupyter/nbclient absent | Download environment; no changes |
| `/home/bahareh/miniforge3` base | 3.14 | No Astropy/NumPy/SciPy/Matplotlib/nbclient import specs | Not suitable |

`environment.json` records actual imported analysis-package versions and interpreter. No package installation, new environment, sudo or system configuration change. Matplotlib and Jupyter runtime caches were redirected to `/tmp` because the home configuration directory is outside the write sandbox. Jupyter initially failed because the sandbox forbids local sockets, then ran successfully with approved escalation. No remote data service or credentials were needed for notebook execution.

The original notebook was stored in the project root but configured to look for `pilot_294866` relative to its runtime directory. Reproduction changes those input/output paths only; all numerical and plotting code remains as in the original. New notebook uses Astropy for general FITS safety. No original notebook is edited.
