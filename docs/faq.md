---
jupyter:
  jupytext:
    cell_metadata_filter: all,-trusted
    notebook_metadata_filter: -all,kernelspec,jupytext
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.19.4
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

<!-- #region -->
# Frequently Asked Questions

## Data Access

<details>
<summary><strong>How can I access PACE data?</strong></summary>

All PACE data (including Level 0 and Level 1 products) is open access and distributed by OB.DAAC (the Ocean Biology Distributed Active Archive Center). There are several ways to access it, depending on your needs:

- **[OB.DAAC file search and direct data access](https://oceandata.sci.gsfc.nasa.gov/api/file_search/)** – Best when you already know exactly which file you want to download; the most efficient method once identified. Excludes data from other DAACs.
- **[Earth Data Search](https://search.earthdata.nasa.gov)** – Discover data using filters such as date range, platform, instrument, and other metadata. Use the **Harmony** subsetting tool to subset and download data directly.
- **[Level 3/Level 4 Browser](https://oceandata.sci.gsfc.nasa.gov/l3/)** – Preview mapped/binned imagery before downloading, with some subsetting capability. Note: "Provisional" here refers to *science* provisional status, not data availability.
- **[Worldview](https://worldview.earthdata.nasa.gov)** – Browse data by layer (e.g., chlorophyll) with a timeline feature; links back to the dataset landing page for download.
- **[SeaDAS](https://www.earthdata.nasa.gov/data/tools/seadas)** – The newest release (SeaDAS 11) includes an Earth Data Cloud/OB Cloud Data Browser that lets you search, view, subset, and download PACE data directly from the cloud (see below for details).
- **[Earthaccess API for Python](https://earthaccess.readthedocs.io/en/stable/)** – Tutorials available on the [**Help Hub**](https://nasa.github.io/oceandata-notebooks/notebooks/oci/oci_data_access.html), ideal for scripting, batch downloads, data subscriptions, and Jupyter notebook workflows.

Choose the method that best fits your specific workflow and data needs. All PACE data, like all NASA data, is free and open to use. A written summary of PACE data access methods is also available on the [**PACE Data Access page**](https://pace.oceansciences.org/access_pace_data.htm).

</details>

<details>
<summary><strong>What's the best way to browse and download PACE images using SeaDAS?</strong></summary>

- Open the **Earth Data Cloud / OB Cloud Data Browser** within **[SeaDAS](https://www.earthdata.nasa.gov/data/tools/seadas)**.
- Select your sensor (e.g., PACE OCI) and processing level. Available product suites depend on the level chosen.
- Filter by date range and bounding box, or select a predefined region (e.g., Black Sea, Caspian Sea).
- Browse search results by hovering over available files.
- You can **download multiple files at once** (up to 100), but **subsetting is only available for Level 2 data**, one file at a time (Level 1B does not support subsetting). Variable-based subsetting is not currently recommended, since it can strip out important data quality flags.
- A future SeaDAS release will let users download direct file links instead of full files, for easier batch processing.

**Comparing data across missions:**
- Download a Level 2 file from each mission of interest.
- Use SeaDAS's **L2 Bin** tool to bin the data, then map each to a common resolution/projection.
- Use the **Co-locate** tool in SeaDAS to combine and compare mapped files from different missions or different years of the same mission.

Note: While SeaDAS has traditionally been an ocean-focused tool, it is increasingly useful for PACE's multidisciplinary (ocean, atmosphere, land) data, since it was developed by the same team behind the mission. **[SeaDAS tutorials](https://nasa.github.io/oceandata-notebooks/sections/seadas-toolbox.html)** are also available on the Help Hub.

</details>

<details>
<summary><strong>Where can I learn more about the PACE mission and its instruments?</strong></summary>

- **[PACE Ocean Science website](pace.gsfc.nasa.gov/)** – Provides in-depth science background for each instrument.
- **[Earth Data Search](https://search.earthdata.nasa.gov)** – Use the search bar on the top-left to type "PACE" and find data collections. Collection information button leads mission resources, instrument details, data sets, and tools (including SeaDAS).
- **[Earth Data Forum](https://forum.earthdata.nasa.gov/viewforum.php?f=7&&DAAC=86&Discipline=&Projects=&ServicesUsage=&keywords=&author=&startDate=&endDate=&bestAnswer=&noReplies=&tagMatch=all&searchWithin=&modClaim=)** – A place to post questions about any mission or dataset. PACE team members actively monitor and respond to questions here, even outside of live events.
- **[Mission overview papers](https://scholar.google.com/scholar?hl=en&as_sdt=0%2C21&q=nasa+pace+mission&btnG=&oq=pace+mis)** – Available for those who prefer in-depth reading.

</details>



---

## Data Subsetting and Size Reduction
<details>
<summary><strong>Is it possible to download a single product from PACE Level 3 files, instead of downloading the full product suite (e.g., IOP, AOP, BGC)?</strong></summary>

Not yet as a fully seamless single-click option, but this capability is actively being developed. Currently, Level 3 product suites (such as IOP, AOP, and BGC) are distributed as combined files rather than one-product-per-file. However, the **Harmony subsetting tool** already allows you to select specific variables and download only the data you need, and this same variable-based subsetting capability is also available for Level 2 data. The team is working to extend more granular product-level extraction capabilities within Earth Data Search as well.

It's worth noting that there is an inherent trade-off here: while one-product-per-file downloads would reduce file size for users who only need a single variable, splitting products into many smaller files could make browsing and searching for data on Earth Data Search more cumbersome for users who need multiple variables at once.

</details>

<details>
<summary><strong>I keep hearing about Harmony for subsetting PACE data, what does it do, and how do I access it?</strong></summary>

Harmony is a NASA web service that lets you customize datasets before downloading — subsetting by geographic region, time range, or variable, as well as reprojecting and reformatting files. You can access it several ways:

- **Through Earth Data Search** – Add a granule to your project, choose "Customize with Harmony" at download, and select the PO.DAAC Level 2 Cloud Subsetter to pick variables, output format, and any filters you've already applied.
- **Directly via Harmony's API**
- **Using the Harmony-Py Python package** – Handles Earthdata login authentication and integrates with the CMR Python wrapper, ideal for Jupyter notebook workflows.
- **Through SeaDAS** – Recent releases (v10/v11) include a built-in cloud data browser that uses Harmony under the hood, with a graphical interface.

A dedicated [dataset subsetting tutorial](https://nasa.github.io/ocean-data-notebooks) covering the Harmony-Py workflow is available on the Help Hub.


</details>

<details>
<summary><strong>Is subsetting really worth it, or should I just download the full files?</strong></summary>

Subsetting can save an enormous amount of storage and download time. In one example, subsetting PACE OCI Level 2 BGC data to a Chesapeake Bay bounding box and selecting only the chlorophyll-a variable reduced 44 granules (~760 MB) down to about 5 MB — a **99.33% reduction**. Similarly, subsetting a global Level 3 monthly map file (134 MB) down to just the Chesapeake Bay region shrank it to about 0.02 MB — a **99.99% reduction**. If you only need data for a specific region, subsetting is almost always worth doing.

</details>

<details>
<summary><strong>Harmony-Py doesn't seem to support subsetting for Level 3 data, is there another way to do this?</strong></summary>

Correct, Harmony-Py currently doesn't support spatial subsetting for Level 3 mapped data. Fortunately, this isn't a big obstacle, since Level 3 products are already gridded to a regular spatial grid, making them easy to subset directly using **Xarray** (e.g., with `.sel()` and slicing). The **[Data Subsetting Help Hub tutorial](https://nasa.github.io/oceandata-notebooks/notebooks/oci/subsetting_with_harmony-py.html)** walks through this: searching for Level 3 monthly composites (e.g., 4 km BGC data) via *earthaccess*, then subsetting and plotting with Xarray.

</details>

<details>
<summary><strong>Is Harmony planned to support Level 3 data, or will that remain limited to Xarray-based workflows?</strong></summary>

Yes, support for Level 3 data in Harmony is planned, though no firm timeline is available yet. Level 2 support exists because another Distributed Active Archive Centers (DAAC) had already built the necessary service into Harmony's cloud hub. PACE's Level 3 files differ structurally from previous missions, and the move to cloud infrastructure requires additional development work. This is an active, ongoing effort.

</details>

<details>
<summary><strong>When subsetting Level 2 data in SeaDAS, why do I lose quality flags if I select individual variables?</strong></summary>

This is a known current limitation: subsetting by variable in SeaDAS (via Harmony) strips out quality flag data along with everything except the selected variable, which isn't ideal since flags are often needed to properly interpret Level 2 data. Until this is resolved, it's best to leave all variables selected when subsetting Level 2 files, and rely on **spatial subsetting only** (e.g., using a bounding box or predefined region like Lake Erie or the Black Sea) rather than variable-based subsetting.

Other current SeaDAS subsetting limitations: it only works on Level 2 data, and only one file at a time (non-subsetted downloads can include up to 100 files at once). Upcoming releases aim to add text-based search filtering and the ability to download stable file links instead of full files, for easier batch processing.

</details>

<details>
<summary><strong>I'm trying to clip a smaller region from PACE data using the Level 3/Level 4 browser's "extract" tool, but I'm not getting all the bands I expect. Is this a known issue?</strong></summary>

Yes, this has been reported as a known issue: using the "extract" function to clip PACE data to a custom region in the Level 3/Level 4 browser has, in some cases, returned only a subset of the expected bands rather than the full set requested. This issue has been raised with the team.

</details>

---

## Data Formats and Availability

<details>
<summary><strong>What is the difference between PACE Level 1B and Level 1C files?</strong></summary>

**Level 1 data** refers to calibrated, geolocated observations at the top of the atmosphere. **Level 2** products are geophysical retrievals derived from Level 1 (e.g., aerosol optical depth), and **Level 3** involves binning data into maps.

PACE's two polarimeters (HARP2 and SPEXone) are **multi-angle instruments**, meaning they observe the same location from multiple viewing angles (forward, downward, backward) as the spacecraft passes overhead. This creates a need to reorganize the raw data so that all angles corresponding to a single point on Earth are grouped together for retrieval algorithms.

- **Level 1B**: Represents top-of-atmosphere observations in their original, per-view format. Can have higher spatial resolution depending on the sensor. For instruments like OCI (a single-view sensor), Level 1B can be used directly since there's no need to reorganize multi-angle views.
- **Level 1C**: A binned, reorganized version of the data where multi-angle views are grouped together for a common location, using a defined spatial grid (5.2 x 5.2 km resolution). This format is primarily needed for the polarimeters (HARP2, SPEXone), since their retrievals depend on having all viewing angles aligned, but also available for OCI for comparisons between all PACE instruments.

As a result:
- OCI aerosol and cloud products are derived from **Level 1B** (higher resolution).
- HARP2 and SPEXone aerosol and cloud products are derived from **Level 1C** (coarser, gridded resolution).

This means Level 1C-derived products are easier to directly compare across instruments.

For more details, refer to:
- The **[PACE Level 1C Technical Memo](https://pace.oceansciences.org/docs/NASA_TM2024219027v12_Level1C.pdf)**, available under **[Documents > Technical Memos](https://pace.oceansciences.org/documents.htm?id=memo)** on the PACE website.
- The **[Level 1A](https://oceancolor.gsfc.nasa.gov/files/PACE_OCI_L1A_Users_Guide.pdf) and [Level 1C](https://oceancolor.gsfc.nasa.gov/files/PACE_L1C_Users_Guide.pdf) User's Guides**, available in the **[technical documents](https://oceancolor.gsfc.nasa.gov/resources/docs/technical/)** section of the Ocean Color website.

</details>

<details>
<summary><strong>Do I need to download both HARP2 Level 1C and Level 2 data instead of just Level 2?</strong></summary>

Certain information available in HARP2 Level 1C data—such as viewing angle information—is not included in the Level 2 product. If your analysis requires this type of metadata, you may need to download both the L1C and L2 granules to obtain the complete set of information needed. To help manage data volume, you can choose to download only the specific variables you need (e.g., absorption coefficient, backscatter coefficient, or water-leaving reflectance) rather than the full file.

</details>

<details>
<summary><strong>Is there a workflow for bringing PACE OCI data into Google Earth Engine?</strong></summary>

Yes. One common workflow involves retrieving PACE OCI surface reflectance, vegetation indices, remote sensing reflectance (aquatic reflectance), and chlorophyll data as NetCDF files, then converting that data to GeoTIFF format using tools such as SeaDAS or SNAP. The resulting GeoTIFFs can then be uploaded into Earth Engine, where no-data values can be removed and the data rescaled as needed to generate usable image collections. Toolkits built on this workflow help make PACE data more broadly accessible to the large existing community of Earth Engine users.

</details>

<details>
<summary><strong>Why is PACE OCI surface reflectance data in 32-bit float format, while remote sensing reflectance (Rrs) data is in 16-bit format?</strong></summary>

Some algorithms require the higher precision of 32-bit float format. This is an active topic of internal discussion, as the team works to balance algorithm precision needs with overall file size. No final resolution has been determined yet.

</details>

<details>
    <summary><strong>Why does it sometimes take a long time for PACE OCI refined (non-near-real-time) monthly and 8-day products to become available?</strong></summary>

The timeline depends on the final calibration and ancillary inputs needed for processing, which have varying delivery dates outside the PACE team's control. In particular, refined products depend on specific ancillary datasets (such as updated GMAO MERRA-2 data), which are released in monthly blocks and aren't always available immediately — for example, June ancillary data may not be released until late July, delaying that month's refined monthly and 8-day composites.

As a result, the time between the end of a given month and the availability of its refined composite can vary — sometimes around the usual one-to-two-month delay, and at other times longer, depending on when the required calibration and ancillary inputs become available. Additional lag can also occur due to reprocessing or other data pipeline complexities.

Near-real-time daily data, by contrast, is generally available with much shorter latency, though without the benefit of the final refined calibration and ancillary inputs used in the refined products.
</details>
<details> <summary><strong>Are there any plans to generate 8-day or monthly composites directly from near-real-time daily data, to reduce the wait for refined products?</strong></summary>

This is under consideration, though it involves some trade-offs. Near-real-time data lacks the final calibration and ancillary inputs used in refined products, so composites built from near-real-time data would not have the same quality as standard refined composites. There is also concern that releasing a longer-period product (like a monthly composite) derived from near-real-time data could cause confusion, since users might assume it represents the same completeness and quality as the standard refined monthly product. The PACE team is evaluating options, including a possible "rolling" near-real-time composite (e.g., a rolling 32-day product), to help bridge this gap while maintaining clarity about data quality and completeness.
</details>


---

## Cloud Computing for PACE Data Access and Analysis

<details>
<summary><strong>What does "cloud computing" mean in the context of NASA's Earth Data Cloud?</strong></summary>

Cloud computing with Earth Data Cloud has two components:

1. **Storage** – NASA's Earth science data (including PACE data) is stored at a commercial data center, specifically in the Amazon Web Services (AWS) US West 2 region.
2. **Processing** – Rather than downloading data to your local machine, you can run your code directly in that same data center using virtualization technologies, bringing your analysis to the data instead of bringing the data to you.

This represents a shift from the "old school" model, where each NASA DAAC operated as a separate archive requiring long download times to your local computer, to a "new school" model where all the data lives in one place and you can process it there directly with much shorter data transfer needs. For more background, see the [Earth Data Cloud Cookbook](https://nasa-openscapes.github.io/earthdata-cloud-cookbook/) and the [Help Hub](https://nasa.github.io/ocean-data-notebooks).

</details>

<details>
<summary><strong>Where can I learn the basics of cloud computing and working with Earth Data Cloud?</strong></summary>

Two key resources are recommended:

- The [**Earth Data Cloud Cookbook**](https://nasa-openscapes.github.io/earthdata-cloud-cookbook/) – A general orientation to Earth Data Cloud created collaboratively by NASA OpenScapes mentors across all NASA DAACs, covering key concepts, tutorials, and how-to guides.
- The [**Help Hub**](https://nasa.github.io/ocean-data-notebooks) – Maintained by the Ocean Ecology Lab, this includes regularly updated tutorials specific to PACE and OB.DAAC datasets (and beyond), all written to run both locally and in the cloud. A recent example is a tutorial on subsetting PACE OCI data, useful since OCI produces very large files and users often only need a portion of the data.

Once you're ready to start working with data directly, the [**earthaccess**](https://earthaccess.readthedocs.io/) Python library is the essential tool for authentication and streaming. It's open-source and has become the standard point of access for Python-based (and some shell-based) workflows with Earth Data Cloud, handling two critical tasks:

1. **Authentication** – Confirms who you are before granting access to data.
2. **Streaming setup** – Establishes the connection needed to stream portions of a file directly, rather than requiring a full download.

</details>

<details>
<summary><strong>What are my options if I want to get into a cloud computing environment to work with PACE data?</strong></summary>

There are two general categories of options:

**1. Externally funded, ready-to-use community hubs** (no cost to you, managed by the nonprofit 2i2c):
- The [**NASA OpenScapes JupyterHub**](https://openscapes.cloud/) – A "cloud playground" primarily intended for workshops and NASA OpenScapes Champions, ideal for exploring what cloud-based Jupyter work is like. PACE researchers interested in access can reach out directly.
- [**CryoCloud JupyterHub**](https://cryointhecloud.com/) – A research-oriented platform, currently free to use, open to the entire geosciences community (not just cryosphere research). Access requires filling out a sign-up form and emailing the CryoCloud leadership team about your research interests.

**2. More customizable platforms** (require more setup, but offer greater flexibility):
- [**NASA Science Cloud**](https://science.data.nasa.gov/science-cloud) – Available to anyone with ROSES funding. Provides a similar JupyterHub-style environment with direct AWS access, plus a support team that can help with technical customization and cost/budget planning for grant proposals. (Note: As of this discussion, ROSES 2026 guidance on cloud computing costs in proposals was still pending, though ROSES 2025 did not address this explicitly.)
- [**Cloud Bank**](https://www.cloudbank.org/) – Open to any US-based researcher (not limited to NSF-funded researchers). Provides credits usable on AWS, Google Cloud, or Microsoft Azure. For Earth Data Cloud work, you'd typically convert these credits to AWS credits, giving you full control over your own custom compute environment.

</details>

<details>
<summary><strong>Does it cost money to access and analyze PACE data in the cloud?</strong></summary>

**Accessing/reading data is free.** NASA covers the storage costs for its data in AWS, and there is no charge for reading that data as long as your compute is happening within the same AWS data center. Similarly, requesting a **spatial or spectral subset of data before downloading is also free** — this counts as a smaller "egress" (data leaving the cloud) rather than as compute/analysis time.

**Analysis/processing time is what may cost money.** As soon as you read data using a virtual computer running in the cloud (e.g., to add two images together, run calculations, etc.), that qualifies as "compute," and you're billed for the time that virtual machine is running — typically by the minute or even microsecond, depending on the type of processor used (e.g., standard CPU vs. GPU).

That said, if you're using an externally funded platform like [CryoCloud](https://cryointhecloud.com/) or [NASA OpenScapes JupyterHub](https://openscapes.cloud/), those costs are already covered by their existing grants, so you likely won't pay anything out of pocket. Costs become more relevant if you set up your own custom environment (e.g., via [NASA Science Cloud](https://science.data.nasa.gov/science-cloud) or [Cloud Bank](https://www.cloudbank.org/) credits) for a specific research budget or grant proposal.

</details>

<details> <summary><strong>When I run a local Python script using my Earthdata credentials (e.g., with earthaccess) to search and access cloud data, is the data being downloaded to my computer, or is my code running in the cloud?</strong></summary>

In a standard local Python workflow — without deliberately provisioning cloud-based compute resources (like a JupyterHub environment) — your code runs on your local machine, not in the cloud.

However, whether data actually gets downloaded depends on how you access it:

- If you use earthaccess.open(), no data is downloaded until you explicitly save something to your local disk. Up until that point, you're simply streaming and interacting with data that remains in the cloud.
- If you use a standard download function instead, the data will be pulled directly to your local machine.

This means users with only Earthdata login credentials (and no separate cloud computing account) can still access and work with PACE data locally through Python — either by streaming portions of a file via earthaccess.open(), or by downloading files outright — without needing a dedicated JupyterHub account.

If you want your processing to happen directly within the cloud environment itself (rather than locally, whether streaming or downloading), you would need to set up and run your code within a cloud compute platform, such as one of the JupyterHub environments described elsewhere in this FAQ.
</details>

<details>
<summary><strong>Can I run L2gen remotely from my local computer using cloud-hosted PACE data?</strong></summary>

No. L2gen currently requires **in-region computing**, meaning it must be run within the same AWS cloud region where the data resides. It cannot stream data over HTTP to a local computer for processing. If you want to use L2gen, you'll need to work within a cloud compute environment (such as SeaDAS) rather than calling it remotely from a local Python installation.

</details>

<details>
<summary><strong>Is there a way to run L2gen-based processing without setting up my own cloud compute environment?</strong></summary>

Yes. **SeaDAS** allows you to search for and access cloud-hosted PACE data, subset it, and process it—including running L2gen—through a Docker image that encapsulates the processor and handles cloud access on your behalf. This provides a way to use L2gen-based processing without needing to independently configure your own AWS compute environment.

</details>

---

## Atmospheric Correction and Aerosols

<details>
<summary><strong>How are atmospheric artifacts and scan-edge errors handled in OCI data?</strong></summary>

PACE applies atmospheric correction (via the L2gen module in SeaDAS) to remove atmospheric and glint effects before deriving ocean color products. At extreme viewing angles (scan edges), longer atmospheric path lengths make correction more challenging, so these areas are currently flagged and masked at Level 3. Future versions may relax this flagging as validation improves.

</details>

<details>
<summary><strong>How does PACE distinguish aerosols from harmful algal blooms (HABs)?</strong></summary>

Atmospheric correction separates aerosol signals from the water surface using specific wavelength bands. Intense algal blooms (e.g., cyanobacteria) can mimic land-like signals in the near-infrared, complicating this separation. PACE's shortwave infrared bands (up to 2.2 microns) help improve this distinction by leveraging strong water absorption at those wavelengths.

</details>

<details>
<summary><strong>Can users adjust processing settings for turbid or inland waters (e.g., lakes)?</strong></summary>

Yes. In SeaDAS, users can adjust L2gen settings such as:

- Relaxing the **cloud threshold** to avoid masking very bright, turbid waters.
- Switching to **shortwave infrared bands** instead of near-infrared bands for atmospheric correction in these conditions.

More information on **[processing data with L2gen](https://nasa.github.io/oceandata-notebooks/notebooks/oci/oci_ocssw_l2gen.html)** is available on the Help Hub

</details>

<details>
<summary><strong>What are the main differences between the aerosol products from PACE's three sensors (OCI, HARP2, SPEXone)?</strong></summary>

All three sensors contribute aerosol-related products, though through different algorithms:

- **OCI** uses the **Unified Aerosol Algorithm (UAA)** and the **UV Aerosol Index**, which build on heritage algorithms from prior missions (VIIRS, MODIS) and combine elements of Dark Target, Deep Blue, and the UV Aerosol Index.
- **HARP2 and SPEXone** (the polarimeters) use **FastMAPOL** and **RemoTAP**, which perform simultaneous retrievals of multiple atmospheric and surface parameters (ocean or land), leveraging additional polarization information for more detailed aerosol characterization. These algorithms are newer and still being refined and matured, though they offer access to more aerosol properties at a coarser spatial resolution.

Aerosol optical depth (or thickness) is produced by all three sensors. Additional algorithms are in development, including **MAIAC**, **GRASP**, and a synergistic multi-sensor algorithm called **MAPP**, which will combine data from all three PACE sensors for the mission's first true synergistic aerosol retrieval.

For more details on specific aerosol products from each sensor, refer to the **[data products table](https://pace.oceansciences.org/data_table.htm)** on the PACE website.

</details>

<details>
<summary><strong>Are there aerosol-related products in the Ocean Color (AOP) product suite as well?</strong></summary>

Yes. Some aerosol information appears as a byproduct of the atmospheric correction process used to derive ocean color (apparent optical properties) products. These aerosol byproducts are not designed for standalone aerosol analysis; they exist primarily to help correct for atmospheric effects and retrieve accurate surface ocean color properties. They can also serve as a useful diagnostic for evaluating ocean color product quality. Users should be cautious about applying these products for dedicated aerosol studies, since they are typically produced only over the open ocean and are not intended as primary aerosol retrievals.

</details>

<details>
<summary><strong>Is there a common approach for applying custom atmospheric correction algorithms (such as Polymer) to PACE data?</strong></summary>

Yes. A common workflow involves scripting a process to download the required Level 1B files, then applying a custom atmospheric correction algorithm (such as Polymer) locally on a computing cluster once the files have been retrieved. This approach provides full control over the atmospheric correction process for specialized research applications outside the standard L2gen pipeline.

</details>

---

## Cloud Products

<details>
<summary><strong>What are the main differences between the cloud products from OCI, HARP2, and SPEXone?</strong></summary>

The differences stem from what each instrument physically measures:

- **OCI** measures **total radiance** (the total energy of incoming radiation), consistent with heritage sensors like MODIS and VIIRS. This provides continuity with established, decades-long cloud climate data records.
- **HARP2 and SPEXone** (polarimeters) measure not only total radiance but also the **polarization** (orientation of the electromagnetic vibrations) of incoming light, and do so from **multiple viewing angles**. This enables new types of retrievals that can reveal **mesoscale cloud structure** in unprecedented detail.

Together, these instruments provide complementary information: OCI extends historical cloud records, while the polarimeters enable new insights into cloud structure and properties that were not previously measurable, expanding overall understanding of cloud systems.

</details>

---

## Phytoplankton Identification, Ocean and Aquatic Products

<details>
<summary><strong>Why are traditional statistical/empirical algorithms used for PACE OCI chlorophyll detection instead of machine learning techniques?</strong></summary>

Traditional empirical algorithms are currently used because they are robust, well-validated, and provide stable performance. Any proposed machine learning algorithm would need to demonstrate not only improved accuracy but also consistent performance across diverse ocean conditions, along with rigorous validation against independent observations. Establishing that level of validation for a global operational product remains a significant challenge. The team remains open to new algorithmic approaches as they mature. More information on the current **[Chlorophyll algorithm](https://oceancolor.gsfc.nasa.gov/files/atbd/atbd-obdaac-chlorophyll-a.pdf)** for PACE OCI on the Earthdata website.

</details>

<details>
<summary><strong>Can PACE data (including pigment data) distinguish between species or only genus/class? Can in situ pigment data help validate or distinguish species?</strong></summary>

It depends on the application and location:

- For large-scale open ocean studies, algorithms are typically designed to distinguish class-level communities (e.g., diatoms, dinoflagellates, haptophytes) rather than species.
- For regional applications—such as identifying a specific harmful algal bloom—algorithms can be tailored to detect a particular species or genus (e.g., *Microcystis* in Lake Erie, *Karenia brevis* on the West Florida shelf).
- Species-level identification across the board is uncommon given the vast diversity within groups (e.g., many diatom species), but particular use cases can achieve this level of specificity.
- In situ pigment sampling (water samples analyzed for pigment content) is essential for validating the algorithms used to derive phytoplankton community composition products.

This remains an active and exciting area of PACE-enabled research.

</details>

<details>
<summary><strong>Are there plans to use backscatter/scattering data for genus- or species-level phytoplankton identification?</strong></summary>

Yes. Absorption and scattering properties differ across phytoplankton communities, and there is published research showing that scattering data can help distinguish specific species (e.g., *Karenia brevis*) from other communities. Scattering data also provides useful information on particle size. This is an active research area.

</details>

<details>
<summary><strong>Is it possible to obtain the phytoplankton absorption coefficient (aph) using PACE, and is it applicable to coastal/estuary studies?</strong></summary>

Yes. The phytoplankton absorption coefficient (aph) is part of the **[Inherent Optical Properties (IOP) product suite](https://www.earthdata.nasa.gov/data/catalog?keyword=PACE%20OCI%20IOP%20Inherent%20Optical%20Properties)**, available via Earth Data Search or the Level 3 browser under the "IOP" short name. It is produced using the GIOP (Generalized Inherent Optical Property) model developed as part of standard Level 2 processing, and a value is generated for every pixel.

It can be applied to coastal and estuarine studies, but caution is advised: GIOP was primarily designed for open ocean conditions, and optically complex coastal waters (due to suspended sediments, dissolved organic matter, etc.) introduce more uncertainty when inverting remote sensing reflectance into IOPs. As a result, aph may be less reliable in coastal areas compared to open ocean waters. Users are encouraged to validate results with in situ data before applying these products to coastal research.

</details>

<details>
<summary><strong>How large does a lake need to be for a harmful algal bloom to be observable/detectable with PACE OCI?</strong></summary>

For reliable harmful algal bloom monitoring, a lake should ideally be at least 5 to 10 times larger than PACE OCI's spatial resolution (approximately 1.2 km at nadir), generally translating to a minimum water body size of about 10 to 25 square kilometers, with blooms covering multiple 1.2 km OCI pixels.

For example, a 7 km² water body would likely be too small to monitor reliably, while a 25 km² water body could provide enough valid water pixels for bloom studies. Caution is also needed near shorelines or ice, since mixed land/water/ice signals within a pixel reduce retrieval accuracy and make it harder to determine the true extent of a bloom. Water depth can also affect detectability.

</details>

---


## Sensor Comparisons (PACE vs. Other Missions)

<details>
<summary><strong>What are the advantages of PACE's NO2 product compared to TROPOMI and TEMPO?</strong></summary>

PACE's NO2 product is trained on TROPOMI NO2 data but offers a key advantage: **finer spatial resolution**. PACE OCI provides roughly 1 km resolution, compared to several kilometers for TROPOMI, making OCI more capable of pinpointing small NO2 sources and plumes.

- **TROPOMI** currently provides the best absolute data quality, making it the preferred choice when quantitative accuracy and precision are the priority.
- **TEMPO** is the only sensor among the three that captures the **diurnal cycle**, making it the best option for diurnal NO2 studies, provided the region of interest is over North America.

</details>

<details>
<summary><strong>How do EMIT and PACE complement each other?</strong></summary>

EMIT is an imaging spectrometer on the International Space Station (ISS) that is hyperspectral from about 380 to 2500 nm (in ~7.5 nm steps), with 60-meter spatial resolution. However, because of its ISS orbit, EMIT only captures data between about ±50 degrees latitude and does not have a regular repeat cycle — it must be manually turned on over areas of interest, so it lacks PACE's frequent (1–2 day) temporal coverage.

PACE and EMIT are considered natural partners for combined analysis: EMIT offers much finer spatial detail (60 m vs. PACE's ~1.2 km pixels), while PACE offers far superior temporal coverage. Using both together helps fill observational gaps — for example, capturing rapidly evolving events (like wildfires) more frequently than EMIT alone could, while still benefiting from EMIT's fine spatial detail when available. This pairing is also a helpful way to introduce PACE to land-focused scientists already familiar with EMIT and hyperspectral data.

</details>

<details>
<summary><strong>Is there a tutorial or notebook series demonstrating how to use PACE and EMIT data together?</strong></summary>

Yes. A notebook series developed with LP DAAC (Land Processes DAAC) colleagues demonstrates how to combine PACE and EMIT data, using a case study of the 2024–2025 wildfires in Grampians National Park, Australia (two fires that merged and burned roughly 130,000 hectares). The series is divided into two parts:

1. **Finding and processing co-located data** (2 notebooks, currently published)
2. **Case study science applications** (2 notebooks, planned for future release)

The first notebook covers searching for and identifying overlapping PACE and EMIT granules in space and time using *earthaccess*, then filtering by cloud cover and temporal/spatial overlap to identify usable matchups (e.g., narrowing 71 initial results down to just a few well-matched granule pairs for pre-fire and post-fire analysis).

The second notebook covers **processing** these matched datasets: merging EMIT granules (often split across multiple tiles due to its narrow swath), masking both datasets for quality (clouds, water), and regridding PACE and EMIT to a common resolution so they become "stackable" for direct comparison — including interactive spectral comparison plots showing vegetation burn signatures before, during, and after the fires.

These notebooks are published on NASA's Earthdata VITALS website, with links also available via the Help Hub.

Learn more: [Earthdata VITALS Website](https://nasa.github.io/VITALS/) | [Help Hub](https://nasa.github.io/oceandata-notebooks/)

</details>

<details>
<summary><strong>Are there bands that PACE OCI is missing that would be useful for fire-related applications, compared to EMIT?</strong></summary>

Yes. PACE OCI lacks certain shortwave infrared (SWIR) bands that EMIT has, including bands sensitive to cellulose absorption, which are important for producing high-fidelity fractional cover products. EMIT has released a fractional cover product using these bands.

While OCI cannot fully replicate this, there are potential workarounds using products like GPP (Gross Primary Productivity) to partition certain vegetation characteristics and approximate a fractional cover product. This remains more of a research topic than an established product. PACE does produce a standard vegetation indices product suite, and there is interest in comparing OCI-derived indices with EMIT's fractional cover data, potentially including sub-pixel analysis in the future.

</details>

<details>
<summary><strong>Is there a difference in the number of overlapping observations between EMIT and PACE across the northern versus southern hemisphere?</strong></summary>

This wasn't fully confirmed during discussion, but EMIT's early mission focus included targeted observations over Australia (related to dust and radiative forcing studies). Since launching in 2022, EMIT is believed to have fairly complete coverage between approximately ±50 degrees latitude. Follow-up verification with a coverage map was planned to confirm hemisphere-specific differences.

</details>

<details>
<summary><strong>How do EarthCare and PACE complement each other?</strong></summary>

EarthCare is a joint ESA/JAXA mission with four sensors that complement PACE well: a Multispectral Imager (passive, narrower swath, higher resolution, visible + thermal bands), an Atmospheric LIDAR, a Cloud Profiling Radar, and a Broadband Radiometer. The active sensors add detailed vertical profile data that pairs nicely with PACE's wide-swath, hyperspectral, and hyperangular instruments (OCI, HARP2, SPEXone).

PACE and EarthCare aren't co-orbital, but their ascending/descending daytime orbits cross paths multiple times per day, creating regular observation overlaps.

</details>

<details>
<summary><strong>Is there a tool to help find and compare matching PACE and EarthCare observations?</strong></summary>

Yes. **PACE EarthCare Matchups** is an open-source Python library that finds, downloads, and compares co-located PACE and EarthCare data. Similar to *earthaccess*, you provide search parameters (products, time range, optional bounding box/offset), and it handles querying both NASA's CMR and ESA's data catalog, checking overlap, downloading, and interpolating data of different dimensionalities (e.g., 2D imagery vs. 1D LIDAR curtains) for direct comparison. A NASA Earthdata account is all you need — no separate ESA login required.

EarthCare data (HDF5) is organized similarly to PACE data, making it fairly easy to work with using standard tools. For product details, see the EarthCare Handbook.

Learn more: [PACE EarthCare Matchups GitHub Repo](https://github.com/seanremy/pace-earthcare-matchups)

</details>

<details>
<summary><strong>Will the proposed GLIMR mission have better shortwave bands than PACE OCI?</strong></summary>

No. GLIMR is currently planned to observe only up to about 750 nanometers (possibly extending slightly into the UV), with no shortwave infrared capability. Adding SWIR bands would require significant engineering trade-offs, including additional cooling, greater spacecraft power, and higher data transfer rates — all of which involve substantial cost. Similar constraints affected PACE's design; for example, a proposed fine-resolution coastal camera and thermal infrared bands were considered but ultimately not included due to data rate and power limitations.

</details>

---

## PACE for Machine Learning

<details>
<summary><strong>What are the best practices for using PACE data in machine learning applications?</strong></summary>

While the ideal approach depends on the specific application, some general best practices include:

- Collect as large a dataset as feasible, since PACE provides extensive daily global data.
- Use **spatial context** rather than isolated pixel samples — for example, extract image patches (e.g., 128 x 128 pixels) around regions of interest.
- Sample **globally** to ensure geographic diversity in your dataset.
- Split training, validation, and test sets **by date/time** rather than by individual instance, to avoid data leakage and ensure your test set remains truly independent.

This is a broad topic, and further guidance can be tailored to specific machine learning applications upon request on the **[Earthdata Forum](https://forum.earthdata.nasa.gov/viewforum.php?f=7&sid=911db1767c205202b974997808fadfcb&DAAC=86&Discipline=&Projects=&ServicesUsage=&keywords=&author=&startDate=&endDate=&bestAnswer=&noReplies=&tagMatch=any&searchWithin=&modClaim=)**.

</details>
<!-- #endregion -->
