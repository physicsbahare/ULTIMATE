# Optional MaNGA observational validation proposal

This is a documentation-based proposal, not an executed observational comparison. No MaNGA science files/catalogues were downloaded and nobody was contacted. The workshop mention of asking Anil does not establish whether the request belongs to ULTIMATE or GECKOS; that ownership remains unresolved. It does not block the DR1 pilot.

## Small, bounded sample

Propose 6–10 nearby star-forming disks, selected before inspecting colour-feature associations, spanning apparent axis ratio and surface brightness. Exclude severe interactions/foreground-star contamination and critical reductions. Require adequate Hβ coverage across a useful disk region, not just a central Hα detection. Separate two development galaxies from the remaining evaluation galaxies; count repeat observations as repeats of a galaxy. These sample size and quality cuts are proposed analysis choices, not SDSS requirements.

## Available public products

The [DR17 data model](https://www.sdss4.org/dr17/manga/manga-data/data-model/) documents DAP MAPS files and HYB10-MILESHC-MASTARSSP: continuum fitting uses binned spectra while emission lines are measured on individual spaxels. Use Hα/Hβ Gaussian flux, inverse-variance and mask channels by header names, not hard-coded channel indices. The [DAP tutorial](https://www.sdss4.org/dr17/manga/manga-tutorials/dap-tutorial/dap-python-tutorial/) illustrates emission-line maps and masks. The DAP also supplies spectral-index information useful for stellar-population checks; indices constrain populations rather than uniquely measure age or metallicity. Request individual MAPS products only after selecting IDs.

The [FIREFLY DR17 VAC](https://www.sdss4.org/dr17/manga/manga-data/manga-firefly-value-added-catalog/) provides spatially resolved model-dependent stellar ages, metallicities and E(B−V), in Voronoi bins. The two full catalogues are about 6.1 GB each, so do not download them for this pilot. The documented small global-property tables omit the resolved maps. Investigate Marvin access or request only selected maps from a collaborator before any large transfer.

The [Pipe3D DR17 documentation](https://www.sdss4.org/dr17/manga/manga-data/manga-pipe3d-value-added-catalog/) provides per-galaxy products with stellar-population, line and absorption-index information, plus validity/foreground-star masks and QCFLAG. Its [data model](https://data.sdss.org/datamodel/files/MANGA_PIPE3D/MANGADRP_VER/PIPE3D_VER/manga.Pipe3D.html) should be checked for the precise stellar-extinction plane, units and uncertainty convention before use. Do not assume Pipe3D A_V and FIREFLY E(B−V) are interchangeable measurements or independent truth.

## Attenuation and quality treatment

Nebular colour excess follows E(B−V)_gas = 2.5/[k(Hβ)−k(Hα)] log10[(F_Hα/F_Hβ)/R_intrinsic]. Adopt and record an attenuation curve and an intrinsic line-ratio model, including sensitivity to gas conditions. Correct foreground Milky Way extinction consistently; underlying Balmer absorption and continuum-fit errors matter. A proposed starting cut is line S/N>5 for both lines, with stronger Hβ cuts as a sensitivity check. Use ionization diagnostics to separate star-forming emission from AGN/LIER-dominated regions. Ratios consistent with zero or negative reddening require uncertainty treatment, not clipping and then claiming a positive signal.

Nebular attenuation samples ionized-gas sightlines; stellar-continuum attenuation is luminosity-weighted and model dependent. Their spatial association with image features is a validation test, not identity or 3D-geometry proof.

## Imaging and resolution matching

[SDSS DR17 access](https://www.sdss4.org/dr17/data_access/) provides optical FITS imaging and access to 2MASS images. This establishes an available route, not adequate NIR depth/resolution for each proposed galaxy. Check each field's J/H/Ks coverage, PSF, variance and surface-brightness depth; deeper NIR coverage is an unresolved sample-selection dependency. Do not equate 2MASS bands with ULTIMATE passbands.

The [DRP documentation](https://www.sdss4.org/dr17/manga/manga-pipeline/) describes reconstructed griz PSF estimates. Read those per observation; never treat the spaxel scale as resolution. Register images to the IFU astrometry and convolve all comparison data to a verified common effective PSF, respecting Voronoi bins. A second native-imaging analysis can show structure that the IFU cannot validate, but cannot label sub-IFU features spectroscopically confirmed. Propagate covariance: [working with MaNGA data](https://www.sdss4.org/dr17/manga/manga-data/working-with-manga-data/) explicitly documents adjacent-spaxel correlations and DRP/DAP quality masks. Do not treat duplicated Voronoi values or adjacent spaxels as independent samples.

Deliverable for a future bounded validation: per-galaxy structure–attenuation association at common resolution, stratified by stellar age/metallicity and surface brightness, with development/evaluation separation and galaxy-level uncertainty. This tests whether an image structure indicator has observational support; it does not supply a dust-free galaxy counterpart.
