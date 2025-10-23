# Overview
[Link de Referência](https://mosqlimate-client.readthedocs.io/en/latest/)

# Mosqlimate client

[![ci](https://github.com/Mosqlimate-project/mosqlimate-client/workflows/ci/badge.svg)](https://github.com/Mosqlimate-project/mosqlimate-client/actions?query=workflow%3Aci)
[![documentation](https://img.shields.io/badge/docs-mkdocs%20material-blue.svg?style=flat)](https://api.mosqlimate.org/docs/)
[![pypi version](https://img.shields.io/pypi/v/mosqlimate-client.svg)](https://pypi.org/project/mosqlient)
[![gitter](https://badges.gitter.im/join%20chat.svg)](https://gitter.im/mosqlimate-client/community)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

client library for the Mosqlimate project data platform.

## Requirements

Mosqlimate client requires Python 3.10 or above.



## Installation

```bash
pip install mosqlient
# if score ou forecast functions are needed:
pip install mosqlient[analyze]
```

## Using from R
Despite `mosqlient` being a Python library, it can be used from R using the `reticulate` package. Here is an example of how to use `mosqlient` from R:

In the examples folder, you can find an [R jupyter notebook](docs/tutorials/Using%20Mosqlient%20from%20R.ipynb) of how to use `mosqlient` from R.



---

# Changelog
[Link de Referência](https://mosqlimate-client.readthedocs.io/en/latest/changelog/)

Release Notes
---

## [1.9.3](https://github.com/Mosqlimate-project/mosqlimate-client/compare/1.9.2...1.9.3) (2025-05-22)


### Bug Fixes

* **bug:** add jupyter kernel creation ([0210c64](https://github.com/Mosqlimate-project/mosqlimate-client/commit/0210c64732d9d808c83e785650664675ba5e7079))
* **bug:** install R in the runner ([8d50939](https://github.com/Mosqlimate-project/mosqlimate-client/commit/8d50939fb16183a39840b8eaca7f54db4313c24b))
* **bug:** register IR kernel ([c2d1b18](https://github.com/Mosqlimate-project/mosqlimate-client/commit/c2d1b1878b061691f5f6be8daa539166c0d8ac8d))
* **bug:** run R demo ([22c9d20](https://github.com/Mosqlimate-project/mosqlimate-client/commit/22c9d206062432212a4457a8657608beceab99ef))
* **bugs:** docs/tutorials/Using Mosqlient from R.ipynb ([1650594](https://github.com/Mosqlimate-project/mosqlimate-client/commit/16505940f3a2bd0ec262ae6b6596a0e7816cdc86))
* **bug:** solve ci.yml ([9afca98](https://github.com/Mosqlimate-project/mosqlimate-client/commit/9afca9860514ca9697500d9df3e353ba42ecd5e4))
* **registry:** replace ADM_level by adm_level ([#76](https://github.com/Mosqlimate-project/mosqlimate-client/issues/76)) ([1053c26](https://github.com/Mosqlimate-project/mosqlimate-client/commit/1053c26abb10fae40456d3aef241d10df22e9dab))

## [1.9.2](https://github.com/Mosqlimate-project/mosqlimate-client/compare/1.9.1...1.9.2) (2025-04-23)


### Bug Fixes

* **climate:** include climate/weekly endpoint ([#70](https://github.com/Mosqlimate-project/mosqlimate-client/issues/70)) ([d1020f2](https://github.com/Mosqlimate-project/mosqlimate-client/commit/d1020f2fbee85f9acd605122a7ea197f419afb12))

## [1.9.1](https://github.com/Mosqlimate-project/mosqlimate-client/compare/1.9.0...1.9.1) (2025-04-14)


### Bug Fixes

* **mosqlient:** minor issue with apply ensemble ([3f4e730](https://github.com/Mosqlimate-project/mosqlimate-client/commit/3f4e730d44519c8aa58a738f633d8b5d22e0aa0c))
* **mosqlient:** type-checks ([83f2667](https://github.com/Mosqlimate-project/mosqlimate-client/commit/83f26674d26d0b31b67686c500fe20ddc2027fb2))

# [1.9.0](https://github.com/Mosqlimate-project/mosqlimate-client/compare/1.8.1...1.9.0) (2025-04-09)


### Bug Fixes

* **baseline:** solve baseline model to work properly after refactor ([19e8861](https://github.com/Mosqlimate-project/mosqlimate-client/commit/19e8861cc219343ee4fd2378491893c6da6ae860))
* **ci:** change pre-commit instruction ([87e7b16](https://github.com/Mosqlimate-project/mosqlimate-client/commit/87e7b16209ed44a64357ce8cfcae3d489f641afe))
* **ci:** update python version in the ci ([de2eda4](https://github.com/Mosqlimate-project/mosqlimate-client/commit/de2eda4f9dab26060e975d13a7ce56b0d9a434f5))
* **mosqlient:** solve type-checking issues ([a28537c](https://github.com/Mosqlimate-project/mosqlimate-client/commit/a28537c08f85d94807e79b5cad4a326f021d9af1))
* **registry:** solve error in delete ([90aa4a2](https://github.com/Mosqlimate-project/mosqlimate-client/commit/90aa4a2c68d28b065ef7377152bd114f93bb3019))


### Features

* **scoring:** add wis in Scorer class ([915104e](https://github.com/Mosqlimate-project/mosqlimate-client/commit/915104e8cda957cf0a68585e2f193a198efa98d3))
* **scoring:** add wis score and create compability of the scores with the new pred elements ([d02e35f](https://github.com/Mosqlimate-project/mosqlimate-client/commit/d02e35fba96e276429f41f07c4e943797a360d75))

## [1.8.1](https://github.com/Mosqlimate-project/mosqlimate-client/compare/1.8.0...1.8.1) (2025-03-26)


### Performance Improvements

* **ensemble:** improve the ensemble performance ([da12ed9](https://github.com/Mosqlimate-project/mosqlimate-client/commit/da12ed96497dbce668aab2369b93c3de2e419b10))

# [1.8.0](https://github.com/Mosqlimate-project/mosqlimate-client/compare/1.7.3...1.8.0) (2025-03-25)


### Features

* **ensemble:** add module to compute ensemble of predictions based on mix of distributions ([0def6a7](https://github.com/Mosqlimate-project/mosqlimate-client/commit/0def6a7d199dd49c6a3acb6bac5812e4d9f35163))

## [1.7.3](https://github.com/Mosqlimate-project/mosqlimate-client/compare/1.7.2...1.7.3) (2025-02-14)


### Bug Fixes

* **docs:** fix errors on docs/ notebooks ([#55](https://github.com/Mosqlimate-project/mosqlimate-client/issues/55)) ([7242f08](https://github.com/Mosqlimate-project/mosqlimate-client/commit/7242f0866739aaec79c4252d4abeee419d55156a))

## [1.7.2](https://github.com/Mosqlimate-project/mosqlimate-client/compare/1.7.1...1.7.2) (2024-12-19)


### Bug Fixes

* **release:** deploy DOI on Zenodo ([#52](https://github.com/Mosqlimate-project/mosqlimate-client/issues/52)) ([9867ee9](https://github.com/Mosqlimate-project/mosqlimate-client/commit/9867ee9ad84716fdd1a7c9b30b9380f42f35119c))

## [1.7.1](https://github.com/Mosqlimate-project/mosqlimate-client/compare/1.7.0...1.7.1) (2024-12-18)


### Bug Fixes

* **release:** bump version to 1.7.1 (fix) ([#51](https://github.com/Mosqlimate-project/mosqlimate-client/issues/51)) ([37a2e2f](https://github.com/Mosqlimate-project/mosqlimate-client/commit/37a2e2f9b7d3b373d6591835d8ba84871b41137a))

# [1.7.0](https://github.com/Mosqlimate-project/mosqlimate-client/compare/1.6.3...1.7.0) (2024-10-30)


### Features

* **Prediction:** include calculate_score to calculate score for individual Predictions ([#47](https://github.com/Mosqlimate-project/mosqlimate-client/issues/47)) ([87757a0](https://github.com/Mosqlimate-project/mosqlimate-client/commit/87757a0ee8ba198ad8c7839d0dae738fcc50ed2e))

## [1.6.3](https://github.com/Mosqlimate-project/mosqlimate-client/compare/1.6.2...1.6.3) (2024-08-23)


### Bug Fixes

* **version:** bump version to 1.6.3 to apply latest commits on PyPI ([#45](https://github.com/Mosqlimate-project/mosqlimate-client/issues/45)) ([ee5e333](https://github.com/Mosqlimate-project/mosqlimate-client/commit/ee5e333d2f004be406b840f357c6fdfea951f256))

## [1.6.2](https://github.com/Mosqlimate-project/mosqlimate-client/compare/1.6.1...1.6.2) (2024-08-23)


### Bug Fixes

* **PredictionDataRowSchema:** rename columns ([#43](https://github.com/Mosqlimate-project/mosqlimate-client/issues/43)) ([44701bc](https://github.com/Mosqlimate-project/mosqlimate-client/commit/44701bcde2f30260108ec7bf8da651b3d9b672a3))

## [1.6.1](https://github.com/Mosqlimate-project/mosqlimate-client/compare/1.6.0...1.6.1) (2024-08-20)


### Bug Fixes

* **Score:** add a minimum value for the log score ([eea4d9d](https://github.com/Mosqlimate-project/mosqlimate-client/commit/eea4d9d61c0f6632ca4c866211c1c4b9288fef55))

# [1.6.0](https://github.com/Mosqlimate-project/mosqlimate-client/compare/1.5.4...1.6.0) (2024-08-15)


### Bug Fixes

* **Scorer:** allow to compute crps and log score to other confidence levels ([79e3fae](https://github.com/Mosqlimate-project/mosqlimate-client/commit/79e3fae7a99ea527effeed676bcb573978d72f95))


### Features

* **score:** add interval score ([434a2e1](https://github.com/Mosqlimate-project/mosqlimate-client/commit/434a2e19f1e7eb367ea63f6a31ef33bb87699c72))

## [1.5.4](https://github.com/Mosqlimate-project/mosqlimate-client/compare/1.5.3...1.5.4) (2024-08-09)


### Bug Fixes

* **version:** bump version to 1.5.4 to apply latest commits on PyPI ([#38](https://github.com/Mosqlimate-project/mosqlimate-client/issues/38)) ([f11e1c1](https://github.com/Mosqlimate-project/mosqlimate-client/commit/f11e1c1707f070784655ff51f7bd3dc7ef7ede38))

## [1.5.3](https://github.com/Mosqlimate-project/mosqlimate-client/compare/1.5.2...1.5.3) (2024-08-09)


### Bug Fixes

* **Model:** remove author_username parameter from upload_model method ([#36](https://github.com/Mosqlimate-project/mosqlimate-client/issues/36)) ([b089631](https://github.com/Mosqlimate-project/mosqlimate-client/commit/b089631f4b9c82368794c26e540d23e2efc98bf6))

## [1.5.2](https://github.com/Mosqlimate-project/mosqlimate-client/compare/1.5.1...1.5.2) (2024-08-09)


### Bug Fixes

* minor error in score.py ([#35](https://github.com/Mosqlimate-project/mosqlimate-client/issues/35)) ([abfce21](https://github.com/Mosqlimate-project/mosqlimate-client/commit/abfce21cf258a9cfb95d210c6e49852bbc0be056))

## [1.5.1](https://github.com/Mosqlimate-project/mosqlimate-client/compare/1.5.0...1.5.1) (2024-08-09)


### Bug Fixes

* **Scorer:** update Scorer to use Prediction object; pep8 format ([#32](https://github.com/Mosqlimate-project/mosqlimate-client/issues/32)) ([1be71a8](https://github.com/Mosqlimate-project/mosqlimate-client/commit/1be71a8765a39b3edc9ac883400a4bd65a6b3345))

# [1.5.0](https://github.com/Mosqlimate-project/mosqlimate-client/compare/1.4.0...1.5.0) (2024-08-07)


### Features

* **package:** parse JSON objects to pydantic schemas ([#29](https://github.com/Mosqlimate-project/mosqlimate-client/issues/29)) ([f167280](https://github.com/Mosqlimate-project/mosqlimate-client/commit/f16728056289b5be45d3d663d82c5e6c9b52e2a0))

# [1.4.0](https://github.com/Mosqlimate-project/mosqlimate-client/compare/1.3.2...1.4.0) (2024-07-18)


### Features

* **config:** replace env variable by a global setting ([#28](https://github.com/Mosqlimate-project/mosqlimate-client/issues/28)) ([370690e](https://github.com/Mosqlimate-project/mosqlimate-client/commit/370690e0088ec8151337abaa7abf97fb24dae472))

## [1.3.2](https://github.com/Mosqlimate-project/mosqlimate-client/compare/1.3.1...1.3.2) (2024-06-25)


### Bug Fixes

* **update_py_version:** update python version to <3.13 ([5bcaa23](https://github.com/Mosqlimate-project/mosqlimate-client/commit/5bcaa23e059cc34524db1fc555b5d02cf8d0f2b4))

## [1.3.1](https://github.com/Mosqlimate-project/mosqlimate-client/compare/1.3.0...1.3.1) (2024-06-25)


### Bug Fixes

* **post:** restrain prediction data to be a pure json only ([#25](https://github.com/Mosqlimate-project/mosqlimate-client/issues/25)) ([513dec0](https://github.com/Mosqlimate-project/mosqlimate-client/commit/513dec040457d71d9772d12f375e5aff11c771f6))

# [1.3.0](https://github.com/Mosqlimate-project/mosqlimate-client/compare/1.2.3...1.3.0) (2024-06-24)


### Bug Fixes

* **dependencies:** ignore jinja2 problem ([#23](https://github.com/Mosqlimate-project/mosqlimate-client/issues/23)) ([836ade6](https://github.com/Mosqlimate-project/mosqlimate-client/commit/836ade6bf9507fe8f9856fd3b4ad22a935315cdb))
* **post:** fix minor errors in post method ([f3a8616](https://github.com/Mosqlimate-project/mosqlimate-client/commit/f3a861649ef249db649c9d6d4c4b8e9a6ed7bf53))
* **release:** mirror python dependency on conda env & poetry ([#24](https://github.com/Mosqlimate-project/mosqlimate-client/issues/24)) ([9269b3d](https://github.com/Mosqlimate-project/mosqlimate-client/commit/9269b3de933d8e4d066724e4f2c892acc333b1e7))


### Features

* **score:** Add first score module ([0a9c8ed](https://github.com/Mosqlimate-project/mosqlimate-client/commit/0a9c8edd4bd2be791617c95415b65839971c3d42))

## [1.2.3](https://github.com/Mosqlimate-project/mosqlimate-client/compare/1.2.2...1.2.3) (2024-06-19)


### Bug Fixes

* **Prediction:** update post_prediction types to accept only JSON serializable objects ([#21](https://github.com/Mosqlimate-project/mosqlimate-client/issues/21)) ([d286b40](https://github.com/Mosqlimate-project/mosqlimate-client/commit/d286b40cb9b5c38d1fd42a9466a4a09809376923))

## [1.2.2](https://github.com/Mosqlimate-project/mosqlimate-client/compare/1.2.1...1.2.2) (2024-06-17)


### Bug Fixes

* **requests:** include first page on results ([#19](https://github.com/Mosqlimate-project/mosqlimate-client/issues/19)) ([4d6062b](https://github.com/Mosqlimate-project/mosqlimate-client/commit/4d6062bcca12d1d13cfbeefa8cc752d4c88f7dbb))

## [1.2.1](https://github.com/Mosqlimate-project/mosqlimate-client/compare/1.2.0...1.2.1) (2024-06-16)


### Bug Fixes

* **baseline:** remove data loader from arima class ([3868fd3](https://github.com/Mosqlimate-project/mosqlimate-client/commit/3868fd3c2becbbc8b77d690b0392a0032a9a4db3))
* **datastore:** implement pydantic; improve code; improve imports; async vs threads benchmark; high level functions ([#17](https://github.com/Mosqlimate-project/mosqlimate-client/issues/17)) ([7ca74a9](https://github.com/Mosqlimate-project/mosqlimate-client/commit/7ca74a9e535d821120bc95336fbb701bf1eb7be5))

# [1.2.0](https://github.com/Mosqlimate-project/mosqlimate-client/compare/1.1.0...1.2.0) (2024-06-11)


### Bug Fixes

* **registry:** create pydantic type validations; improve registry endpoint; improve struct; include registry.Prediction; include update_model to registry.Model ([#9](https://github.com/Mosqlimate-project/mosqlimate-client/issues/9)) ([7768ee5](https://github.com/Mosqlimate-project/mosqlimate-client/commit/7768ee5ae61d0683f612d6ecdd0e675595e1d91f))


### Features

* **baseline:** first baseline model ([973c2d0](https://github.com/Mosqlimate-project/mosqlimate-client/commit/973c2d0c3d5c56b97971b3f737279a9e4cd69864))

# [1.1.0](https://github.com/Mosqlimate-project/mosqlimate-client/compare/1.0.1...1.1.0) (2024-05-28)


### Features

* **datastore:** Add functions to get the data from the datastore ([#8](https://github.com/Mosqlimate-project/mosqlimate-client/issues/8)) ([8573932](https://github.com/Mosqlimate-project/mosqlimate-client/commit/857393242b6b35a915476c1984a38426ab6ab8be))

## [1.0.1](https://github.com/Mosqlimate-project/mosqlimate-client/compare/1.0.0...1.0.1) (2024-05-27)


### Bug Fixes

* **package:** make params parse run after params type checker ([#7](https://github.com/Mosqlimate-project/mosqlimate-client/issues/7)) ([e4d5437](https://github.com/Mosqlimate-project/mosqlimate-client/commit/e4d54370648c8c14ced17be24cad5ef07bc0ce7a))

# 1.0.0 (2024-05-27)


### Bug Fixes

* **package:** add option to change between prod and env environments ([#6](https://github.com/Mosqlimate-project/mosqlimate-client/issues/6)) ([86796ed](https://github.com/Mosqlimate-project/mosqlimate-client/commit/86796ed8c1b370f9f0a1aec977b7eb332aedb02a))

# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

<!-- insertion marker -->



---

# Tutorial - Datastore
[Link de Referência](https://mosqlimate-client.readthedocs.io/en/latest/tutorials/API/datastore/)

# Interacting with the Mosqlimate datastore
[📥 Download Notebook](https://github.com/Mosqlimate-project/mosqlimate-client/blob/main/docs/tutorials/API/datastore.ipynb)

Fetching data from the Mosqlimate API. Below, you can find example code to pull data from both the `Infodengue` and `Climate` datasets.

```python
import os
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("API_KEY")
```

```python
import mosqlient
```

## InfoDengue

```python
mosqlient.get_infodengue?
```

```python
mosqlient.get_infodengue(
    api_key = api_key,
    disease =  "dengue",
    start_date = "2022-01-01",
    end_date = "2023-01-01",
    geocode = 4108304
).head()
```

To get the data for all the cities in a state, don't fill the `geocode` field, as in the example below:

```python
mosqlient.get_infodengue(
    api_key = api_key,
    disease =  "dengue",
    start_date = "2022-01-01",
    end_date = "2023-01-01", 
    uf = 'AL'
).head()
```

## Climate

```python
mosqlient.get_climate?
```

```python
mosqlient.get_climate(
    api_key = api_key,
    start_date = "2022-01-01",
    end_date = "2022-01-01", 
    uf = "RJ",
).head()
```

```python
mosqlient.get_climate(
    api_key = api_key,
    start_date = "2022-01-01",
    end_date = "2023-01-01", 
    geocode = 4108304,
)
```

## Climate Weekly

```python
mosqlient.get_climate_weekly?
```

```python
mosqlient.get_climate_weekly(
    api_key = api_key,
    start = "202201",
    end = "202301", 
    geocode = 4108304,
)
```

## Episcanner

```python
mosqlient.get_episcanner?
```

```python
mosqlient.get_episcanner(
    api_key = api_key,
    uf = "SP"
)
```

## Mosquito

```python
mosqlient.get_mosquito?
```

```python
mosqlient.get_mosquito(
    api_key = api_key,
    date_start = "2024-01-01",
    date_end = "2024-12-31",
    state = "MG",
)
```



---

# Reference - Infodengue data
[Link de Referência](https://mosqlimate-client.readthedocs.io/en/latest/reference/infodengue/)


### `mosqlient.datastore._infodengue_get_impl`

**Arquivo Fonte:** `mosqlient/datastore/_infodengue_get_impl.py`
```python
__all__ = ["get_infodengue"]

from typing import Optional, Literal
from datetime import date

import pandas as pd

from mosqlient import types
from .models import Infodengue


def get_infodengue(
    api_key: str,
    disease: Literal["dengue", "zika", "chikungunya"],
    start_date: date | str,
    end_date: date | str,
    uf: Optional[types.UF] = None,
    geocode: Optional[int] = None,
) -> pd.DataFrame:
    """
    Fetch InfoDengue Data from Mosqlimate API for dengue, zika, or chikungunya.

    Parameters
    ----------
        api_key : str
            API key used to authenticate with the Mosqlimate service.
        disease : {'dengue', 'zika', 'chikungunya'}
            The arbovirus to retrieve data for.
        start_date : date or str
            Start date of the data range (as a `datetime.date` or ISO format string).
        end_date : date or str
            End date of the data range (as a `datetime.date` or ISO format string).
        uf : types.UF, optional
            The Brazilian state abbreviation (e.g., 'SP', 'RJ'). If provided without `geocode`, filters by state.
        geocode : int, optional
            IBGE geocode of a municipality. If provided, overrides `uf`.

    Returns
    -------
    pandas.DataFrame
        DataFrame containing the epidemiological time series data for the specified region and time period.
        Detailed descriptions of each column in the DataFrame can be found in the official API documentation:
        https://api.mosqlimate.org/docs/datastore/GET/infodengue/

    Notes
    -----
    Either `uf` or `geocode` must be provided to specify the target geographic area.

    Examples
    --------
    >>> get_infodengue(
    ...     api_key="your_api_key",
    ...     disease="dengue",
    ...     start_date="2023-01-01",
    ...     end_date="2023-03-01",
    ...     uf="RJ"
    ... )
    """

    return pd.DataFrame(
        Infodengue.get(
            api_key=api_key,
            disease=disease,
            start=start_date,
            end=end_date,
            uf=uf,
            geocode=geocode,
        )
    )

```



---

# Reference - Climate data
[Link de Referência](https://mosqlimate-client.readthedocs.io/en/latest/reference/climate/)


### `mosqlient.datastore._climate_get_impl`

**Arquivo Fonte:** `mosqlient/datastore/_climate_get_impl.py`
```python
__all__ = ["get_climate", "get_climate_weekly"]


from typing import Optional
from datetime import date

import pandas as pd

from mosqlient import types
from .models import Climate, ClimateWeekly


def get_climate(
    api_key: str,
    start_date: date | str,
    end_date: date | str,
    uf: Optional[types.UF] = None,
    geocode: Optional[int] = None,
) -> pd.DataFrame:
    """
    Retrieve historical climate data from the Mosqlimate API for a specific region and date range.

    Parameters
    ----------
        api_key : str
            API key used to authenticate with the Mosqlimate service.
        start_date : date or str
            Start date of the data range (as a `datetime.date` or ISO format string).
        end_date : date or str
            End date of the data range (as a `datetime.date` or ISO format string).
        uf : types.UF, optional
            The Brazilian state abbreviation (e.g., 'SP', 'MG'). If provided and `geocode` is not, filters by state.
        geocode : int, optional
            IBGE geocode of a municipality. If provided, overrides `uf`.

    Returns
    -------
        pandas.DataFrame
            DataFrame containing daily climate data. Detailed descriptions of each column in the DataFrame can be found in the official API documentation:
            https://api.mosqlimate.org/docs/datastore/GET/climate/#output_items

    Notes
    -----
    - Either `uf` or `geocode` must be provided to define the target location.

    Examples
    --------
    >>> get_climate(
    ...     api_key="your_api_key",
    ...     start_date="2023-01-01",
    ...     end_date="2023-01-31",
    ...     geocode=3550308
    ... )
    """

    return pd.DataFrame(
        Climate.get(
            api_key=api_key,
            start=start_date,
            end=end_date,
            uf=uf,
            geocode=geocode,
        )
    )


def get_climate_weekly(
    api_key: str,
    start: str,
    end: str,
    uf: Optional[types.UF] = None,
    geocode: Optional[int] = None,
    macro_health_code: Optional[int] = None,
) -> pd.DataFrame:
    """
    Retrieve historical climate data weekly aggregated

    Parameters
    ----------
        api_key : str
            API key used to authenticate with the Mosqlimate service.
        start : str
            Start epiweek in YYYYWW format (example: 202501).
        end : str
            End epiweek in YYYYWW format (example: 202501).
        uf : str, optional
            The Brazilian state abbreviation (e.g., 'SP', 'MG').
        geocode : int, optional
            IBGE geocode of a municipality.
        macro_health_code : int, optional
            Macro Health IBGE geocode. Example: 1101

    Returns
    -------
        pandas.DataFrame
            DataFrame containing daily climate data. Detailed descriptions of
            each column in the DataFrame can be found in the official API
            documentation:
            https://api.mosqlimate.org/docs/datastore/GET/climate-weekly/

    Notes
    -----
    - Either `uf` or `geocode` or `macro_health_code` must be provided.

    Examples
    --------
    >>> get_climate_weekly(
    ...     api_key="your_api_key",
    ...     start="202401",
    ...     end="202402",
    ...     geocode=3550308
    ... )
    """

    return pd.DataFrame(
        ClimateWeekly.get(
            api_key=api_key,
            start=start,
            end=end,
            uf=uf,
            geocode=geocode,
            macro_health_code=macro_health_code,
        )
    )

```



---

# Reference - Score
[Link de Referência](https://mosqlimate-client.readthedocs.io/en/latest/reference/score/)


### `mosqlient.scoring.score`

**Arquivo Fonte:** `mosqlient/scoring/score.py`
```python
import numpy as np
import pandas as pd
import altair as alt
from typing import Optional
from numpy.typing import NDArray
from scipy.stats import lognorm
from mosqlient import get_prediction_by_id
from scoringrules import crps_normal, crps_lognormal, logs_normal
from mosqlient.prediction_optimize import get_df_pars
from sklearn.metrics import mean_squared_error, mean_absolute_error


def evaluate_point_metrics(y_true, y_pred, metric):
    """
    Evaluate multiple sklearn metrics on given true and predicted values.

    Parameters:
    -------------
    y_true (array-like): True values.
    y_pred (array-like): Predicted values.
    metrics (str): Options: ['MAE', 'MSE'] .

    Returns:
    Scores.
    """

    if metric == "MAE":

        m = mean_absolute_error

    if metric == "MSE":

        m = mean_squared_error

    score = m(y_true, y_pred)

    return score


def compute_interval_score(
    lower_bound, upper_bound, observed_value, alpha=0.05
):
    """
    Calculate the interval score for a given prediction interval and observed value.

    Parameters:
    ------------------
    lower_bound: float | np.array
        The lower bound of the prediction interval.
    upper_bound: float | np.array
        The upper bound of the prediction interval.
    observed_value: float | np.array
        The observed value.
    alpha: float
        The significance level of the interval. Default is 0.05 (for 95% prediction intervals).

    Returns:
    -----------
    float or np.array: The interval score.
    """

    interval_width = upper_bound - lower_bound

    # Compute penalties
    penalty_lower = 2 / alpha * np.maximum(0, lower_bound - observed_value)
    penalty_upper = 2 / alpha * np.maximum(0, observed_value - upper_bound)

    penalty = penalty_lower + penalty_upper

    return interval_width + penalty


def compute_wis(
    df: pd.DataFrame,
    observed_value: NDArray[np.float64],
    w_0: float = 1 / 2,
    w_k: Optional[NDArray[np.float64]] = None,
) -> NDArray[np.float64]:
    """
    Calculate the weighted interval score for a given prediction dataframe and observed value. In the dataframe the column `pred``
    must represent the median and each prediction interval must be enconded as `lower_{1-alpha}*100` and `upper_{1-alpha}*100`,
    where alpha is the significance level of the interval.

    Parameters:
    ------------------
    df:  pd.DataFrame
        The lower bound of the prediction interval.
    observed_value: float | np.array
        The observed value.
    w_0: float
        Initial weight.
    w_k: Optional | np.array
        Weights for each prediction interval, if None the weights are computed based on the
        prediction intervals (w_k = alpha_k/2).

    Returns:
    -----------
    float or np.array:
        The weighted interval score.
    """
    observed_value = np.asarray(observed_value)
    if observed_value.ndim == 0:
        observed_value = observed_value.reshape(1)

    lower_cols = [col for col in df.columns if col.startswith("lower_")]
    alphas = (
        1 - (np.array([float(col.split("_")[-1]) for col in lower_cols])) / 100
    )
    K = len(alphas)

    if w_k is None:
        w_k = alphas / 2
    elif len(w_k) != K:
        raise ValueError(
            f"Weights length {len(w_k)} doesn't match intervals count {K}"
        )

    interval_scores = np.zeros_like(observed_value, dtype=np.float64)

    for alpha, weight in zip(alphas, w_k):
        level = int((1 - alpha) * 100)
        interval_scores += weight * compute_interval_score(
            lower_bound=df[f"lower_{level}"].values,
            upper_bound=df[f"upper_{level}"].values,
            observed_value=observed_value,
            alpha=alpha,
        )

    median_error = np.abs(observed_value - df["pred"].values.reshape(-1))
    return (w_0 * median_error + interval_scores) / (K + 0.5)


def plot_bar_score(data: pd.DataFrame, score: str) -> alt.Chart:
    """
    Function to plot a bar chart based on scorer.summary dataframe

    Parameters:
    --------------
    data: pd.DataFrame
    score: str
        Valid options are: ['mae', 'mse', 'crps', 'log_score']
    """
    data = data.reset_index()
    data["id"] = data["id"].astype(str)

    bar_chart = (
        alt.Chart(data)
        .mark_bar()
        .encode(
            x=alt.X("id:N", axis=alt.Axis(labelAngle=360)).title("Model"),
            y=alt.Y(f"{score}:Q").title(score),
            color=alt.Color("id", legend=alt.Legend(title="Model")),
        )
        .properties(
            title=f"{score} score",
            width=400,
            height=300,
        )
    )

    return bar_chart


def plot_score(
    data: pd.DataFrame, df_melted: pd.DataFrame, score: str = "CRPS"
) -> alt.VConcatChart:
    """
    Function that returns an Altair panel with the time series of cases and the
    time series of the score for each model.

    Parameters
    ----------
    data: pd.DataFrame
        The DataFrame with the time series of cases must contain the columns
        `date` and `casos`.
    df_melted : pd.DataFrame
        The DataFrame must contains the columns:
        * date: with the date';
            * variable: with the models name;
        * '{score}_score': with the score value
    score: str
        Name of the score metric. Available options include: ['CRPS','interval','wis','log']
    """

    if score == "CRPS":
        title = "CRPS score"
        subtitle = "Lower is better"

    if score == "interval":
        title = "Interval score"
        subtitle = "Lower is better"

    if score == "wis":
        title = "WIS"
        subtitle = "Lower is better"

    if score == "log":
        title = "Log score"
        subtitle = "Bigger is better"

    timedata = (
        alt.Chart(data)
        .mark_line()
        .encode(x="date", y="casos", color=alt.value("black"))
        .properties(width=400, height=300)  # Set the width  # Set the height
    )

    # Create a selection that chooses the nearest point & selects based on x-value
    nearest = alt.selection_point(
        nearest=True, on="pointerover", fields=["date"], empty=False
    )

    graph_score = (
        alt.Chart(df_melted)
        .mark_point(filled=False)
        .encode(
            x="date",
            y=f"{score}_score",
            color=alt.Color("variable", legend=alt.Legend(legendX=100)),
        )
        .properties(width=400, height=250)  # Set the width  # Set the height
    )

    # Transparent selectors across the chart. This is what tells us
    # the x-value of the cursor
    selectors = (
        alt.Chart(df_melted)
        .mark_point()
        .encode(  # TODO: Not used
            x="date",
            opacity=alt.value(0),
        )
        .add_params(nearest)
    )

    # Draw points on the line, and highlight based on selection
    points = graph_score.mark_point().encode(
        opacity=alt.condition(nearest, alt.value(1), alt.value(0))
    )

    # Draw a rule at the location of the selection
    columns = list(df_melted.variable.unique())
    tooltip = [
        alt.Tooltip(c, type="quantitative", format=".2f") for c in columns
    ]
    tooltip.insert(0, alt.Tooltip("date:T", title="Date"))
    rules = (
        alt.Chart(df_melted)
        .transform_pivot("variable", value=f"{score}_score", groupby=["date"])
        .mark_rule(color="gray")
        .encode(
            x="date",
            opacity=alt.condition(nearest, alt.value(0.3), alt.value(0)),
            tooltip=tooltip,
        )
        .add_params(nearest)
    )

    return timedata.properties(
        width=400, height=150, title="New cases"
    ) & alt.layer(  # Set the width  # Set the height
        graph_score, points, rules
    ).properties(
        title={"text": title, "subtitle": subtitle}
    )


class Scorer:
    """
    A class to compare the score of the models.

    Attributes
    ----------

    df_true: pd.DataFrame
        DataFrame of the cases provided by the user.


    filtered_df_true: pd.DataFrame
        DataFrame of the cases provided by the user filtered according
        to the interval of the predictions or with the `set_date_range` method .

    ids: Optional[list[int]]
        The list of the predictions id that will be compared


    dict_df_ids: dict[pd.DataFrame]
        A dict of DataFrames of the predictions. If the key is int it refers
        to the ids passed in the init. If it is `pred` it refers to the
        dataframe of the predictions provided by the user.

    filtered_dict_df_ids: dict[pd.DataFrame]
        A dict of DataFrames of the predictions. If the key is int it refers to
        the ids passed in the init. If it is `pred` it refers to the dataframe
        of the predictions provided by the user. The DataFrames are filtered
        according to the interval of the predictions or with the
        `set_date_range` method.

    min_date: str
        Min date that will include the information of the df_true and predictions.

    max_date: str
        Max date that will include the information of the df_true and predictions.

    mae : dict
        Dict where the keys are the id of the models or `pred` when a
        dataframe of predictions is provided by the user, and the values of
        the dict are the mean absolute error.

    mse: dict
        Dict where the keys are the id of the models or `pred` when a
        dataframe of predictions is provided by the user, and the values of the
        dict are the mean squared error.

    crps: tuple of dicts
        Dict where the keys are the id of the models or `pred` when a
        dataframe of predictions is provided by the user, and the values of the
        dict are the scores computed.

        The first dict contains the CRPS score computed for every predicted
        point, and the second one contains the mean values of the CRPS score
        for all the points.

        The CRPS computed assumes a normal distribution.

    log_score: tuple of dicts
        Dict where the keys are the id of the models or `pred` when a
        dataframe of predictions is provided by the user, and the values of the
        dict are the scores computed.

        The first dict contains the log score computed for every predicted
        point, and the second one contains the mean values of the log score for
        all the points.

        The log score computed assumes a normal distribution.


    wis: tuple of dicts
        Dict where the keys are the id of the models or `pred` when a
        dataframe of predictions is provided by the user, and the values of the
        dict are the scores computed.

        The first dict contains the weighted interval score computed for every predicted
        point, and the second one contains the mean values of the weighted interval score
        for all the points.

    summary: pd.DataFrame
        DataFrame where the keys are the id of the models or `pred` when a
        dataframe of predictions is provided by the user, and the columns are
        the scores: mae, mse, and the mean of crps, log_score, interval score
        and weighted interval score.

    Methods
    -------
    start_date_range():
        Train the model.
    plot_predictions():
        Function that returns an Altair panel (alt.Chart) with the time series
        of cases and the predictions for each model.
    plot_crps():
        alt.Chart: Method that returns an Altair panel with the time series of
        cases and the time series of the CRPS score for each model.
    plot_log_score():
        alt.Chart: Method that returns an Altair panel with the time series of
        cases and the time series of the log score for each model.
    plot_interval_score():
        alt.Chart: Method that returns an Altair panel with the time series of
        cases and the time series of the interval score for each model.
    plot_wis():
        alt.Chart: Method that returns an Altair panel with the time series of
        cases and the time series of the weighted interval score for each model.
    plot_mae():
        alt.Chart : Bar chart of the MAE score for each prediction.
    plot_mse():
        alt.Chart : Bar chart of the MSE score for each prediction.
    """

    def __init__(
        self,
        api_key: str,
        df_true: pd.DataFrame,
        ids: Optional[list[int] | list[str]] = None,
        pred: Optional[pd.DataFrame] = None,
        dist: str = "log_normal",
        fn_loss: str = "median",
        conf_level: float = 0.90,
    ):
        """
        Parameters
        ----------
        df_true: pd.DataFrame
            DataFrame with the columns `date` and `casos`.
        ids : list[int]
            List of the predictions ids that it will be compared.
        pred: pd.DataFrame
            Pandas Dataframe already in the format accepted by the platform
            that will be computed the score.
        dist : {'normal', 'log_normal'}, optional, default='log_normal'
            The type of distribution used for parameter estimation.
        fn_loss : {'median', 'lower'}, optional, default='median'
            Specifies the method for parameter estimation:
            - 'median': Fits the log-normal distribution by minimizing `pred` and `upper` columns.
            - 'lower': Fits the log-normal distribution by minimizing `lower` and `upper` columns.
        conf_level: float.
            The confidence level of the predictions of the columns upper and lower.
        """

        # input validation data
        cols_df_true = ["date", "casos"]

        if not set(cols_df_true).issubset(set(list(df_true.columns))):
            raise ValueError(
                "Missing required keys in the df_true:"
                f"{set(cols_df_true).difference(set(list(df_true.columns)))}"
            )

        df_true.date = pd.to_datetime(df_true.date)
        # Ensure all the dates has the same lenght
        min_dates = [min(df_true.date)]
        max_dates = [max(df_true.date)]

        dict_df_ids = {}

        if pred is not None:
            cols_preds = [
                "date",
                f"lower_{int(100*conf_level)}",
                "pred",
                f"upper_{int(100*conf_level)}",
            ]
            if not set(cols_preds).issubset(set(list(pred.columns))):
                raise ValueError(
                    "Missing required keys in the pred:"
                    f"{set(cols_preds).difference(set(list(pred.columns)))}"
                )

            pred = get_df_pars(
                pred.copy(), conf_level=conf_level, dist=dist, fn_loss=fn_loss
            )

            dict_df_ids["pred"] = pred
            pred.date = pd.to_datetime(pred.date)
            min_dates.append(min(pred.date))
            max_dates.append(max(pred.date))

        if (ids is None or len(ids) == 0) and (pred is None):
            raise ValueError(
                "It must be provide and id or DataFrame to be compared"
            )

        if ids is not None:
            ids = [str(id_) for id_ in ids]
            for id_ in ids:
                prediction = get_prediction_by_id(api_key=api_key, id=int(id_))

                if not prediction:
                    raise ValueError(f"No Prediction found for id: {id_}")

                df_ = prediction.to_dataframe()
                df_ = df_.dropna(axis=1)
                df_ = df_.sort_values(by="date")
                df_.date = pd.to_datetime(df_.date)
                df_ = get_df_pars(
                    df_.copy(),
                    conf_level=conf_level,
                    dist=dist,
                    fn_loss=fn_loss,
                )
                dict_df_ids[id_] = df_
                min_dates.append(min(df_.date))
                max_dates.append(max(df_.date))

        min_dates = pd.to_datetime(min_dates)
        max_dates = pd.to_datetime(max_dates)
        min_date = max(min_dates)
        max_date = min(max_dates)

        # updating the dates interval
        df_true = df_true.loc[
            (df_true.date >= min_date) & (df_true.date <= max_date)
        ]
        df_true = df_true.sort_values(by="date")
        df_true.reset_index(drop=True, inplace=True)

        for id_ in dict_df_ids.keys():
            df_id = dict_df_ids[id_]
            df_id = df_id.loc[
                (df_id.date >= min_date) & (df_id.date <= max_date)
            ]
            df_id = df_id.sort_values(by="date")
            dict_df_ids[id_] = df_id

        self.df_true = df_true
        self.filtered_df_true = df_true
        self.ids = ids
        self.dict_df_ids = dict_df_ids
        self.filtered_dict_df_ids = dict_df_ids
        self.min_date = min_date
        self.max_date = max_date
        self.dist = dist
        self.conf_level = conf_level

    def set_date_range(self, start_date: str, end_date: str) -> None:
        """
         This method will redefine the interval of dates used to compute the
         scores.
         The new dates provided must be in the interval defined by the
         `__init__` method that ensures the df_true and predictions are in the
         same interval. You can access these values by score.min_date and
         score.max_date.

        Parameters
        --------------
        start_date: str
            The new start date used to compute the scores.
        end_date: str
            The new end date used to compute the scores.
        """

        if (self.min_date > pd.to_datetime(start_date)) or (
            self.max_date < pd.to_datetime(start_date)
        ):
            raise ValueError(
                "The start and end date must be between "
                + f"{self.min_date} and {self.max_date}."
            )

        df_true = self.df_true
        dict_df_ids = self.dict_df_ids

        self.filtered_df_true = df_true.loc[
            (df_true.date >= pd.to_datetime(start_date))
            & (df_true.date <= pd.to_datetime(end_date))
        ]

        for id_ in dict_df_ids.keys():
            df_id = dict_df_ids[id_]
            df_id = df_id.loc[
                (df_id.date >= pd.to_datetime(start_date))
                & (df_id.date <= pd.to_datetime(end_date))
            ]
            dict_df_ids[id_] = df_id

        self.filtered_dict_df_ids = dict_df_ids

        return None

    @property
    def mae(
        self,
    ):
        """
        dict: Dict, where the keys are the id of the models or `pred` when a
        dataframe of predictions is provided by the user, and the values of the
        dict are the mean absolute error.
        """
        ids = self.ids
        dict_df_ids = self.filtered_dict_df_ids
        df_true = self.filtered_df_true

        scores = {}

        for id_ in dict_df_ids.keys():

            scores[id_] = evaluate_point_metrics(
                df_true.casos, y_pred=dict_df_ids[id_].pred, metric="MAE"
            )

        return scores

    @property
    def mse(
        self,
    ):
        """
        dict: Dict, where the keys are the id of the models or `pred` when a
        dataframe of predictions is provided by the user, and the values of the
        dict are the mean squared error.
        """

        ids = self.ids
        dict_df_ids = self.filtered_dict_df_ids
        df_true = self.filtered_df_true

        scores = {}

        for id_ in dict_df_ids.keys():

            scores[id_] = evaluate_point_metrics(
                df_true.casos, y_pred=dict_df_ids[id_].pred, metric="MSE"
            )
        return scores

    @property
    def crps(
        self,
    ):
        """
        tuple of dict: Dict where the keys are the id of the models or `pred`
        when a dataframe of predictions is provided by the user,
        and the values of the dict are the scores computed.

        The first dict contains the CRPS score computed for every predicted
        point, and the second one contains the mean values of the CRPS score
        for all the points.

        The CRPS computed assumes a normal distribution.
        """

        ids = self.ids
        dist = self.dist
        dict_df_ids = self.filtered_dict_df_ids
        df_true = self.filtered_df_true

        scores_curve = {}

        scores_mean = {}

        for id_ in dict_df_ids.keys():

            df_id_ = dict_df_ids[id_]

            if dist == "normal":
                score = crps_normal(
                    df_true.casos,
                    df_id_.mu,
                    df_id_.sigma,
                )
            if dist == "log_normal":
                score = crps_lognormal(
                    df_true.casos,
                    df_id_.mu,
                    df_id_.sigma,
                )

            scores_curve[id_] = pd.Series(score, index=df_true.date)

            scores_mean[id_] = np.mean(score)

        self.crps_curve = scores_curve

        return scores_curve, scores_mean

    @property
    def log_score(
        self,
    ):
        """
        tuple of dict: Dict where the keys are the id of the models or `pred`
        when a dataframe of predictions is provided by the user, and the values
        of the dict are the scores computed.

        The first dict contains the log score computed for every predicted
        point, and the second one contains the mean values of the log score
        for all the points.

        The log score computed assumes a normal distribution.
        """

        ids = self.ids
        dict_df_ids = self.filtered_dict_df_ids
        df_true = self.filtered_df_true
        dist = self.dist

        scores_curve = {}
        scores_mean = {}

        for id_ in dict_df_ids.keys():

            df_id_ = dict_df_ids[id_]

            if dist == "normal":
                score = logs_normal(
                    df_true.casos,
                    df_id_.mu,
                    df_id_.sigma,
                    negative=False,
                )
            if dist == "log_normal":
                score = lognorm.logpdf(
                    df_true.casos.values,
                    s=df_id_.sigma.values,
                    scale=np.exp(df_id_.mu.values),
                )

            # truncated the output
            score = np.maximum(score, np.repeat(-100, len(score)))

            scores_curve[id_] = pd.Series(score, index=df_true.date)
            scores_mean[id_] = np.mean(score)

        self.log_curve = scores_curve

        return scores_curve, scores_mean

    @property
    def interval_score(
        self,
    ):
        """
        tuple of dict: Dict where the keys are the id of the models or `pred`
        when a dataframe of predictions is provided by the user,
        and the values of the dict are the scores computed.

        The first dict contains the interval score computed for every predicted
        point, and the second one contains the mean values of the interval score
        for all the points.
        """

        ids = self.ids
        dict_df_ids = self.filtered_dict_df_ids
        df_true = self.filtered_df_true
        conf_level = self.conf_level

        scores_curve = {}

        scores_mean = {}

        for id_ in dict_df_ids.keys():

            df_id_ = dict_df_ids[id_]

            score = compute_interval_score(
                df_id_[f"lower_{int(100*conf_level)}"].values,
                df_id_[f"lower_{int(100*conf_level)}"].values,
                df_true.casos.values,
                alpha=1 - conf_level,
            )

            scores_curve[id_] = pd.Series(score, index=df_true.date)

            scores_mean[id_] = np.mean(score)

        self.interval_score_curve = scores_curve

        return scores_curve, scores_mean

    @property
    def wis(self, w_0=0.5, w_k=None):
        """
        tuple of dict: Dict where the keys are the id of the models or `pred`
        when a dataframe of predictions is provided by the user,
        and the values of the dict are the scores computed.

        The first dict contains the weighted interval score computed for every predicted
        point, and the second one contains the mean values of the weighted interval score
        for all the points.
        """

        ids = self.ids
        dict_df_ids = self.filtered_dict_df_ids
        df_true = self.filtered_df_true

        scores_curve = {}

        scores_mean = {}

        for id_ in dict_df_ids.keys():

            df_id_ = dict_df_ids[id_]

            score = compute_wis(
                df=df_id_,
                observed_value=df_true.casos.values,
                w_0=w_0,
                w_k=w_k,
            )

            scores_curve[id_] = pd.Series(score, index=df_true.date)

            scores_mean[id_] = np.mean(score)

        self.wis_score_curve = scores_curve

        return scores_curve, scores_mean

    @property
    def summary(
        self,
    ):
        """
        pd.DataFrame: DataFrame where the keys are the id of the models or
        `pred` when a dataframe of predictions is provided by the user, and
        the columns are the scores: mae, mse, and the mean of crps, log_score,
        interval_score and weighted interval score.
        """
        sum_scores = {}

        sum_scores["mae"] = self.mae

        sum_scores["mse"] = self.mse

        sum_scores["crps"] = self.crps[1]

        sum_scores["log_score"] = self.log_score[1]

        sum_scores["interval_score"] = self.interval_score[1]

        sum_scores["wis"] = self.wis[1]

        df_score = pd.DataFrame.from_dict(sum_scores, orient="columns")

        df_score.index.name = "id"

        return df_score

    def plot_mae(
        self,
    ) -> alt.Chart:
        """
        Bar chart of the MAE score for each prediction.
        """

        return plot_bar_score(self.summary, "mae")

    def plot_mse(
        self,
    ) -> alt.Chart:
        """
        Bar chart of the MSE score for each prediction.
        """

        return plot_bar_score(self.summary, "mse")

    def plot_crps(
        self,
    ) -> alt.VConcatChart:
        """
        alt.Chart: Function that returns an Altair panel with the time series
        of cases and the time series of the CRPS score for each model
        """

        crps_ = self.crps_curve

        df_crps = pd.DataFrame()

        for v in crps_.keys():

            df_crps[str(v)] = crps_[v]

        df_crps.reset_index(inplace=True)

        df_melted = pd.melt(
            df_crps, id_vars="date", value_vars=list(map(str, crps_.keys()))
        )
        df_melted = df_melted.rename(columns={"value": "CRPS_score"})

        return plot_score(self.df_true, df_melted, score="CRPS")

    def plot_log_score(
        self,
    ) -> alt.VConcatChart:
        """
        alt.Chart: Function that returns an Altair panel with the time series
        of cases and the time series of the Log score for each model
        """

        crps_ = self.log_curve

        df_crps = pd.DataFrame()

        for v in crps_.keys():

            df_crps[str(v)] = crps_[v]

        df_crps.reset_index(inplace=True)

        df_melted = pd.melt(
            df_crps, id_vars="date", value_vars=list(map(str, crps_.keys()))
        )
        df_melted = df_melted.rename(columns={"value": "log_score"})

        return plot_score(self.df_true, df_melted, score="log")

    def plot_interval_score(
        self,
    ) -> alt.VConcatChart:
        """
        alt.Chart: Function that returns an Altair panel with the time series
        of cases and the time series of the CRPS score for each model
        """

        interval_ = self.interval_score_curve

        df_interval = pd.DataFrame()

        for v in interval_.keys():

            df_interval[str(v)] = interval_[v]

        df_interval.reset_index(inplace=True)

        df_melted = pd.melt(
            df_interval,
            id_vars="date",
            value_vars=list(map(str, interval_.keys())),
        )
        df_melted = df_melted.rename(columns={"value": "interval_score"})

        return plot_score(self.df_true, df_melted, score="interval")

    def plot_wis(
        self,
    ) -> alt.VConcatChart:
        """
        alt.Chart: Function that returns an Altair panel with the time series
        of cases and the time series of the wis score for each model
        """

        wis_ = self.wis_score_curve

        df_wis = pd.DataFrame()

        for v in wis_.keys():

            df_wis[str(v)] = wis_[v]

        df_wis.reset_index(inplace=True)

        df_melted = pd.melt(
            df_wis,
            id_vars="date",
            value_vars=list(map(str, wis_.keys())),
        )
        df_melted = df_melted.rename(columns={"value": "wis_score"})

        return plot_score(self.df_true, df_melted, score="wis")

    def plot_predictions(
        self, show_ci: bool = True, width: int = 400, height: int = 300
    ) -> alt.Chart:
        """
        Function that returns an Altair panel (alt.Chart) with the time series
        of cases and the predictions for each model

        Parameters
        ---------------
        show_ci :bool
            If True it shows the confidence interval.
        width: int
            width of the plot
        width: int
            height of the plot
        """

        dict_df_ids = self.filtered_dict_df_ids
        df_true_ = self.filtered_df_true
        df_true_.loc[:, "legend"] = "Data"

        if show_ci:
            title = "Median and 95% confidence interval"
        else:
            title = "Median of predictions"

        df_to_plot = pd.DataFrame()

        for id_ in dict_df_ids.keys():

            df_ = dict_df_ids[id_]

            df_.loc[:, "model"] = id_

            df_to_plot = pd.concat([df_to_plot, df_])

        df_to_plot["model"] = df_to_plot["model"].astype(str)

        data = (
            alt.Chart(df_true_)
            .mark_circle(size=60)
            .encode(
                x="date:T",
                y="casos:Q",
                color=alt.Color(
                    "legend:N",
                    scale=alt.Scale(range=["black"]),
                    legend=alt.Legend(title=None),
                ),
            )
            .properties(
                width=width, height=height
            )  # Set the width  # Set the height
        )

        # here we define the plot of the right figure
        timeseries = (
            alt.Chart(df_to_plot, title=title)
            .mark_line()
            .encode(
                x=alt.X("date:T").title("Dates"),
                y=alt.Y("pred:Q").title("New cases"),
                color=alt.Color("model", legend=alt.Legend(title="Model")),
            )
        )

        # here we create the area that represent the confidence interval of the
        # predicitions
        timeseries_conf = timeseries.mark_area(
            opacity=0.25,
        ).encode(
            x="date:T",
            y="lower:Q",
            y2="upper:Q",
            color=alt.Color("model", legend=None),
        )

        nearest = alt.selection_point(
            nearest=True, on="pointerover", fields=["date"], empty=False
        )

        # Draw points on the line, and highlight based on selection
        points = timeseries.mark_point().encode(
            color=alt.Color("model", legend=None),
            opacity=alt.condition(nearest, alt.value(1), alt.value(0)),
        )

        df_true_ = df_true_.rename(columns={"casos": "pred"})

        df_true_["model"] = "cases"

        df_to_plot = pd.concat([df_to_plot, df_true_])

        columns = list(df_to_plot.model.unique())
        tooltip = [
            alt.Tooltip(c, type="quantitative", format=".0f") for c in columns
        ]
        tooltip.insert(0, alt.Tooltip("date:T", title="Date"))

        rules = (
            alt.Chart(df_to_plot)
            .transform_pivot("model", value="pred", groupby=["date"])
            .mark_rule(color="gray")
            .encode(
                x="date",
                opacity=alt.condition(nearest, alt.value(0.3), alt.value(0)),
                tooltip=tooltip,
            )
            .add_params(nearest)
        )

        if show_ci:

            final = (
                data + timeseries + timeseries_conf + points + rules
            ).resolve_scale(color="independent")

        else:
            final = alt.layer(data, timeseries, points, rules).resolve_scale(
                color="independent"
            )

        return final

```



---