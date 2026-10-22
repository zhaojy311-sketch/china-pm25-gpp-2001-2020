# External data sources

The manuscript names the products below, but the existing project does not provide a complete raw-file manifest, download script, checksum list, access date, or exact product-version record. These details must be reconstructed with the original analysts before release.

| Product | Intended variables | Provider/access | Redistribution note |
|---|---|---|---|
| GOSIF-GPP v2 | GPP | [UNH archive](http://data.globalecology.unh.edu/data/GOSIF-GPP_v2/) | Link and cite; verify provider terms before redistributing files |
| ChinaHighPM2.5 / CHAP | PM2.5 | [Zenodo DOI 10.5281/zenodo.6398971](https://doi.org/10.5281/zenodo.6398971) | Cite the dataset version used; preserve license and access conditions |
| GLASS LAI v6 | LAI | [GLASS download page](https://www.glass.hku.hk/download.html) | Record exact product, resolution, version, and provider terms |
| GLASS PAR | PAR | [GLASS PAR archive](https://glass.hku.hk/archive/PAR/) | Record exact version, resolution, and scale factor |
| PANDA-China | NTL | [DOI 10.11888/Socioeco.tpdc.271202](https://doi.org/10.11888/Socioeco.tpdc.271202) | Provider download may require registration; cite the dataset |
| ERA5-Land | temperature, RH/VPD inputs | [CDS dataset](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land) | CDS terms apply; cite DOI 10.24381/cds.e2161bac |
| 1-km monthly precipitation for China | precipitation | [TPDC record](https://www.tpdc.ac.cn/en/data/faae7605-a0f2-4d18-b28f-5cee413766a2/) | Current record states CC BY-NC-SA 4.0; do not assume commercial-compatible redistribution |

## Missing acquisition details

- Exact filenames and checksums used for 2001–2020.
- Access dates and account/authentication requirements.
- Spatial resolutions used before harmonization.
- Scale factors, fill values, quality-control flags, and temporal aggregation.
- Reprojection/resampling method, target grid, China mask, and treatment of missing pixels.
- Exact derivation of RH and VPD if not read directly from a product.
- Administrative-boundary source and license.

Raw data should remain outside Git. The final repository should provide download/preprocessing scripts or a machine-readable manifest whenever the provider allows automated access.
