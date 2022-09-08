# env-manager

## Project information
[![PyPI - Version](https://img.shields.io/pypi/v/env-manager.svg)](https://pypi.org/project/env-manager)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/env-manager.svg)](https://pypi.org/project/env-manager)
[![conda version](https://img.shields.io/conda/vn/conda-forge/env-manager.svg)](https://www.anaconda.com/conda-forge/env-manager)
[![download count](https://img.shields.io/conda/dn/conda-forge/env-manager.svg)](https://www.anaconda.com/conda-forge/env-manager)

## Build status
[![Windows status](https://github.com/spyder-ide/env-manager/workflows/Windows%20tests/badge.svg)](https://github.com/spyder-ide/env-manager/actions?query=workflow%3A%22Windows+tests%22)
[![Linux status](https://github.com/spyder-ide/env-manager/workflows/Linux%20tests/badge.svg)](https://github.com/spyder-ide/env-manager/actions?query=workflow%3A%22Linux+tests%22)
[![MacOS status](https://github.com/spyder-ide/env-manager/workflows/Macos%20tests/badge.svg)](https://github.com/spyder-ide/env-manager/actions?query=workflow%3A%22Macos+tests%22)
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

You will need to setup the `ENV_BACKEND_EXECUTABLE` environmental variable in order to use a `conda-like` manager. The environmental variable should point to a conda or mamba executable. For example, if you have micromamba downloaded on Windows you should set `ENV_BACKEND_EXECUTABLE=<path to micromama executable>/micromamba.exe`. After that you should be able to run the tests with:

```console
pytest -vv
```

* To check the command line options you need to run:

```console
env-manager --help
```

## License

`env-manager` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
