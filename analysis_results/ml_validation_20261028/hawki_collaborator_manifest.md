# Reduced HAWK-I/GRAAL products and references for possible collaboration

Manifest only; no large file packaging, transfer, raw reduction or new download.

Official ESO NGC3256 programme 60.A-9475(A) reduced image: ADP.2018-02-14T09:20:46.500. Variance: .501. Confidence: .502. Existing target-centred Jan6 cutouts are `../ml_feasibility_20261027/hawki/reduced_jan6_image.fits`, `reduced_jan6_varmap.fits`, `reduced_jan6_weightmap.fits`; combined 64.18 MiB. Science BUNIT ADU; VARMAP semantics are squared image units despite inherited header ADU; confidence is not inverse variance. Download hashes, checksums, cutout/WCS and URLs: original `reduced_download_log.json`. Three OB association trees are certified complete; this does not establish local pipeline dependencies or independent reduction quality.

`hawki_reduced_product_manifest.csv` lists available official reduced observations. `hawki_calibration_reference_manifest.csv` lists associated calibration references, not a claim that all calibration files are locally present. Original empirical measurements, masks, source fits, caveats and 2MASS comparisons remain in `../ml_feasibility_20261027/hawki/hawki_empirical_calibration_report.md`.

Relevant empirical numbers: 103 compact candidates median FWHM 0.3166 arcsec, beta 4.753 and q 0.8199; nine quality-selected 2MASS associations median FWHM 0.2935 arcsec and beta 3.7415. Adjacent background rho_x=0.2753, rho_y=0.2932. At R=32 pixels, aperture noise / (sigma_pixel sqrt(N))=3.4213. Selection and field variation matter; these are not ULTIMATE specifications or dust truth.

Calibration references: [ESO collection](https://doi.eso.org/10.18727/archive/34), [release description](https://www.eso.org/rm/api/v1/public/releaseDescriptions/87), [HAWK-I calibration cascade](https://www.eso.org/observing/dfo/quality/HAWKI/pipeline/pipe_calib.html).
