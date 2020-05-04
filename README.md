# Carpyncho client for Python

> Python client for Carpyncho VVV dataset collection.

[![Build Status](https://travis-ci.org/carpyncho/carpyncho-py.svg?branch=master)](https://travis-ci.org/carpyncho/carpyncho-py)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.3779502.svg)](https://doi.org/10.5281/zenodo.3779502)
[![Python 3](https://img.shields.io/badge/python-3.7+-blue.svg)](https://badge.fury.io/py/carpyncho)
[![BSD-3](https://img.shields.io/badge/License-BSD3-blue.svg)](https://www.tldrlegal.com/l/bsd3)
[![Documentation Status](https://readthedocs.org/projects/carpyncho-py/badge/?version=latest)](https://carpyncho-py.readthedocs.io/en/latest/?badge=latest)
[![PyPI](https://img.shields.io/pypi/v/carpyncho)](https://pypi.org/project/carpyncho/)

[![Logo](https://github.com/carpyncho/carpyncho.github.io/raw/master/static/logo.png)](https://carpyncho.github.io/)

This library access as a [Pandas DataFrame](https://pandas.pydata.org/) all the data of the web version of
Carpyncho [https://carpyncho.github.io/](https://carpyncho.github.io/).

## Code

The entire source code of is hosted in GitHub
[https://github.com/carpyncho/carpyncho-py/](https://github.com/carpyncho/carpyncho-py/)

## License

Carpyncho is under
[The BSD-3 License](https://github.com/carpyncho/carpyncho-py/blob/master/LICENSE)

The BSD 3-clause license allows you almost unlimited freedom with the software so long as you include the BSD copyright and license notice in it (found in Fulltext).

## Citation

If you use Carpyncho in a scientific publication, we would appreciate
citations to the following paper:

> Cabral, J. B., Ramos, F., Gurovich, S., & Granitto, P. (2020).
> Automatic Catalog of RRLyrae from ∼ 14 million VVV Light Curves:
> How far can we go with traditional machine-learning?
> https://arxiv.org/abs/2005.00220

Bibtex entry

```bib
@Article{cabral:2020,
  author      = {Juan B. Cabral AND Felipe Ramos AND Sebastián Gurovich AND Pablo Granitto},
  title       = {
    Automatic Catalog of RRLyrae from $\sim$ 14 million VVV
    Light Curves: How far can we go with traditional machine-learning?},
  version     = {1},
  date        = {2020-05-01},
  eprinttype  = {arxiv},
  eprintclass = {astro-ph.IM, astro-ph.SR, cs.LG, stat.ML},
  eprint      = {http://arxiv.org/abs/2005.00220v1},
  url         = {http://arxiv.org/abs/2005.00220v1}
}
```

## Installation

This is the recommended way to install carpyncho.

### Installing  with pip

Make sure that the Python interpreter can load carpyncho code.
The most convenient way to do this is to use virtualenv, virtualenvwrapper, and pip.

After setting up and activating the virtualenv, run the following command:

``` console
$ pip install carpyncho
...
```

That should be it all.

### Installing the development version

If you’d like to be able to update your carpyncho code occasionally with the latest bug fixes and improvements, follow these instructions:

Make sure that you have Git installed and that you can run its commands from a shell.
(Enter *git help* at a shell prompt to test this.)

Check out carpyncho main development branch like so:

``` console
$ git clone https://github.com/carpyncho/carpyncho-py.git carpyncho
...
```

This will create a directory *carpyncho* in your current directory.

Then you can proceed to install with the commands

```console
$ cd carpyncho
$ pip install -e .
...
```

## Documentation

The full documentation of the project are available in
[https://carpyncho-py.readthedocs.io/](https://carpyncho-py.readthedocs.io/)

## Contact

For bugs or question please contact

> **Juan B. Cabral:** [jbcabral@unc.edu.ar](jbcabral@unc.edu.ar)
