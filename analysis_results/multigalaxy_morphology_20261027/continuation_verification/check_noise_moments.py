"""Independent aggregate Poisson and split-read moment check; no study writes."""
from pathlib import Path
import sys
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import observe


def run():
    _, dusty, _ = observe.load(294866, 'O1')
    geometry = observe.p.make_geometry(.1, 'glao')
    rates, _ = observe.p.render(dusty, geometry)
    analytic = observe.p.variance(rates, 1.)
    rng = np.random.default_rng(9134)
    rows = []
    for j, band in enumerate(observe.p.INST):
        source = float(np.median(rates[j][geometry['roi']]))
        background = band['background_e_s_pixel'] + band['dark_e_s']
        exposure, reads = 3600., 60
        variance = ((source + background) * exposure + reads * band['read_noise_e']**2) / exposure**2
        samples = (rng.poisson((source + background) * exposure, 100000)
                   - (source + background) * exposure
                   + rng.normal(0, np.sqrt(reads) * band['read_noise_e'], 100000)) / exposure
        ratio = samples.var(ddof=1) / variance
        mean_z = samples.mean() / np.sqrt(variance / len(samples))
        assert abs(ratio - 1) < .025 and abs(mean_z) < 4
        np.testing.assert_allclose(np.median(analytic[j][geometry['roi']]), variance, rtol=1e-12)
        rows.append(dict(band=observe.BANDS[j], variance_ratio=ratio,
                         mean_z=mean_z, draws=len(samples), reads=reads, passed=True))
    result = pd.DataFrame(rows)
    result.to_csv(HERE/'fresh_noise_moment_validation.csv', index=False)
    print(result.to_string(index=False))


if __name__ == '__main__':
    run()
