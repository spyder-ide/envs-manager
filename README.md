# env-manager

[![PyPI - Version](https://img.shields.io/pypi/v/env-manager.svg)](https://pypi.org/project/env-manager)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/env-manager.svg)](https://pypi.org/project/env-manager)
[![conda version](https://img.shields.io/conda/vn/conda-forge/env-manager.svg)](https://www.anaconda.com/conda-forge/env-manager)
[![download count](https://img.shields.io/conda/dn/conda-forge/env-manager.svg)](https://www.anaconda.com/conda-forge/env-manager)
[![codecov](https://codecov.io/gh/spyder-ide/env-manager/branch/main/graph/badge.svg?token=H2GZWHIL43)](https://codecov.io/gh/spyder-ide/env-manager)

-----

**Table of Contents**

- [Installation](#installation)
    - [PyPI](#pypi)
    - [Conda](#conda)
- [Development](#development)
- [License](#license)

## Installation

*Note:* This package is not available yet for installation but it will be in the coming months.

### PyPI

```console
pip install env-manager
```

### Conda

```console
conda install -c conda-forge env-manager
```

## Development

* Fork and clone the repo. To clone:

```console
git clone <link to your fork.git>
cd env-manager
```

* Create a Python environment and activate it. For example with conda:

```console
conda env create -n env-manager --file requirements/environment.yml
conda activate env-manager
```

* Install development version:

```console
pip install -e .
```

* Setup pre-commit:

```console
pre-commit install
```

* To run the test:

```console
pytest -vv
```

* To check the command line options you need to run:

```console
env-manager --help
```

## License

`env-manager` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
