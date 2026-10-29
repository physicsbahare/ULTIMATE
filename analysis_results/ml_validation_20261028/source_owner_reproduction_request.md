# Minimal source-product reconciliation experiment

Prepared specification only. No message has been sent and no files have been transferred.

Use an original old zero-projected-dust control (e.g. subhalo13, O1) with its exact historical stellar/source particle lists, BC03/MAPPINGS settings, SKIRT executable/version, filter transmission files and .ski configuration. Archive image labels and units alone are insufficient to identify the operator.

1. Hold source SEDs and spatial projection settings fixed. Integrate each source spectrum independently through the historical g/J/Ks response, including the response-weighting convention and pivot-wavelength conversion.
2. Produce analytic ImportedSourceLuminosityProbe projections with convolve=false and convolve=true. Record the characteristic/pivot wavelength and units. Current software defaults do not establish the historical run setting.
3. Produce explicit NoMedium instrument images with exactly the same source SEDs/filters. Repeat at least three independent photon seeds and two packet counts (including the historical1e9 value). Do not invent packet errors from a single run.
4. Compare full160-kpc fluxes, matched R12 and frozen adaptive apertures, radial growth curves, pixel correlation/smoothing response and C/R50. Preserve signed differences. Match projection/smoothing kernels explicitly.
5. Separately test whether any birth-cloud template/source-spectrum differences remain between nominally clear and dusty constructions. A zero projected diffuse map does not prove the entire transfer volume/source template is identical.

Discriminants: a seed-independent offset removed by matching spectral convolution supports an operator mismatch; variance decreasing with packet count supports Monte Carlo noise; conserved full-field flux with aperture/morphology residuals supports spatial projection differences. Source-owner configuration/SED/filter evidence is required before identifying any specific cause. No universal source-control subtraction is justified by the present atlas alone.
