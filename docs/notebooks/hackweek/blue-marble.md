---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.19.5
kernelspec:
  name: python3
  display_name: Python 3 (ipykernel)
  language: python
license:
  id: NASA-1.3
  name: NASA Open Source Agreement
  url: https://github.com/nasa/oceandata-notebooks/raw/refs/heads/main/LICENSE
notice: 'Copyright © 2024 United States Government as represented by the Administrator
  of

  the National Aeronautics and Space Administration.  All Rights Reserved.


  Disclaimer:


  No Warranty: THE SUBJECT SOFTWARE IS PROVIDED "AS IS" WITHOUT ANY WARRANTY OF ANY

  KIND, EITHER EXPRESSED, IMPLIED, OR STATUTORY, INCLUDING, BUT NOT LIMITED TO, ANY

  WARRANTY THAT THE SUBJECT SOFTWARE WILL CONFORM TO SPECIFICATIONS, ANY IMPLIED WARRANTIES

  OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, OR FREEDOM FROM INFRINGEMENT,

  ANY WARRANTY THAT THE SUBJECT SOFTWARE WILL BE ERROR FREE, OR ANY WARRANTY THAT
  DOCUMENTATION,

  IF PROVIDED, WILL CONFORM TO THE SUBJECT SOFTWARE.  THIS AGREEMENT DOES NOT, IN
  ANY

  MANNER, CONSTITUTE AN ENDORSEMENT BY GOVERNMENT AGENCY OR ANY PRIOR RECIPIENT OF

  ANY RESULTS, RESULTING DESIGNS, HARDWARE, SOFTWARE PRODUCTS OR ANY OTHER APPLICATIONS

  RESULTING FROM USE OF THE SUBJECT SOFTWARE.  FURTHER, GOVERNMENT AGENCY DISCLAIMS

  ALL WARRANTIES AND LIABILITIES REGARDING THIRD-PARTY SOFTWARE, IF PRESENT IN THE

  ORIGINAL SOFTWARE, AND DISTRIBUTES IT "AS IS."


  Waiver and Indemnity:  RECIPIENT AGREES TO WAIVE ANY AND ALL CLAIMS AGAINST THE
  UNITED

  STATES GOVERNMENT, ITS CONTRACTORS AND SUBCONTRACTORS, AS WELL AS ANY PRIOR RECIPIENT.

  IF RECIPIENT''S USE OF THE SUBJECT SOFTWARE RESULTS IN ANY LIABILITIES, DEMANDS,

  DAMAGES, EXPENSES OR LOSSES ARISING FROM SUCH USE, INCLUDING ANY DAMAGES FROM PRODUCTS

  BASED ON, OR RESULTING FROM, RECIPIENT''S USE OF THE SUBJECT SOFTWARE, RECIPIENT
  SHALL

  INDEMNIFY AND HOLD HARMLESS THE UNITED STATES GOVERNMENT, ITS CONTRACTORS AND SUBCONTRACTORS,

  AS WELL AS ANY PRIOR RECIPIENT, TO THE EXTENT PERMITTED BY LAW.  RECIPIENT''S SOLE

  REMEDY FOR ANY SUCH MATTER SHALL BE THE IMMEDIATE, UNILATERAL TERMINATION OF THIS

  AGREEMENT.'
---

```{code-cell} ipython3
import fsspec
```

```{code-cell} ipython3
fsspec.config.conf["s3"] = {
"default_cache_type": "blockcache",
"default_block_size": 2**22
}
```

```{code-cell} ipython3
import earthaccess
import xarray as xr
```

```{code-cell} ipython3
tspan = ("2024-08", '2024-08')
results = earthaccess.search_data(short_name="PACE_OCI_L3M_SFREFL", granule_name="*.MO.*.0p1deg.*", temporal=tspan)
```

```{code-cell} ipython3
paths = earthaccess.open(results)
```

```{code-cell} ipython3
dataset = xr.open_dataset(paths[0])
```

```{code-cell} ipython3
dataset
```

```{code-cell} ipython3
rgb = dataset["rhos"].sel({"wavelength": [645, 555, 440]}, method="nearest")
```

```{code-cell} ipython3
plot = rgb.plot.imshow()
```

```{code-cell} ipython3
import numpy as np
from PIL import Image, ImageEnhance

rgb
scale = 0.01
vmin = 0
vmax = 1.1
gamma = 1
contrast = 1.1
brightness = 1
sharpness = 1.1
saturation = 1

da = rgb.where(rgb > 0)
da = np.log(da / scale) / np.log(1 / scale)
da = da.clip(vmin, vmax)
da = (da - da.min()) / (da.max() - da.min())
da = da * gamma
da = da * 255
da = da.where(da.notnull(), 0).astype("uint8")
img = Image.fromarray(da.data)
enhancer = ImageEnhance.Contrast(img)
img = enhancer.enhance(contrast)
enhancer = ImageEnhance.Brightness(img)
img = enhancer.enhance(brightness)
enhancer = ImageEnhance.Sharpness(img)
img = enhancer.enhance(sharpness)
enhancer = ImageEnhance.Color(img)
img = enhancer.enhance(saturation)
rgb[:] = np.array(img) / 255
```

```{code-cell} ipython3
plot = rgb.plot.imshow()
```

```{code-cell} ipython3

```
