---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.17.2
kernelspec:
  name: python3
  display_name: Python 3 (ipykernel)
  language: python
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
