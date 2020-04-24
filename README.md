# Carpyncho client for python

[![Build Status](https://travis-ci.org/carpyncho/carpyncho-py.svg?branch=master)](https://travis-ci.org/carpyncho/carpyncho-py)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.3762842.svg)](https://doi.org/10.5281/zenodo.3762842)
[![Python 3](https://img.shields.io/badge/python-3.7+-blue.svg)](https://badge.fury.io/py/carpyncho)
[![BSD-3](https://img.shields.io/badge/License-BSD3-blue.svg)](https://tldrlegal.com/license/bsd-3-clause-license-(revised))

## License

Carpyncho is under
[The BSD-3 License](https://github.com/carpyncho/carpyncho-py/blob/master/LICENSE)

The BSD 3-clause license allows you almost unlimited freedom with the software so long as you include the BSD copyright and license notice in it (found in Fulltext).

## Citation


Please cite:

>    J.B.Cabral. (2020, April 23). carpyncho/carpyncho-py: First version (no docs) (Version 0.0.1). Zenodo. http://doi.org/10.5281/zenodo.3762842


``` bibtext
    @software{juan_bc_2020_3762842,
        author       = {J.B. Cabral},
        title        = {carpyncho/carpyncho-py: First version (no docs)},
        month        = apr,
        year         = 2020,
        publisher    = {Zenodo},
        version      = {0.0.1},
        doi          = {10.5281/zenodo.3762842},
        url          = {https://doi.org/10.5281/zenodo.3762842}
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
```

That should be it all.

### Installing the development version

If you’d like to be able to update your carpyncho code occasionally with the latest bug fixes and improvements, follow these instructions:

Make sure that you have Git installed and that you can run its commands from a shell.
(Enter *git help* at a shell prompt to test this.)

Check out carpyncho main development branch like so:

``` console
$ git clone https://github.com/carpyncho/carpyncho-py.git carpyncho
```

This will create a directory *carpyncho* in your current directory.

Then you can proceed to install with the commands

```console
$ cd carpyncho
$ pip install -e .
```

## Command line interface (`CLI`)

After install carpyncho you also have a command line app to download the
data as `csv`/`xlsx`/`parquet`/`pickle`.

```console

$ carpyncho --help
Usage: carpyncho command [args...]

Carpyncho console client.

Explore and download the entire https://carpyncho.github.io/ catalogs from your command line.

Commands:
  catalog-info       Retrieve the information about a given catalog.
  download-catalog   Retrives a catalog from th Carpyncho dataset collection.
  has-catalog        Check if a given catalog and tile exists.
  list-catalogs      Show the available catalogs for a given tile.
  list-tiles         Show available tiles.
  version            Print Carpyncho version.

This software is under the BSD 3-Clause License.
Copyright (c) 2020, Juan Cabral.
For bug reporting or other instructions please check:
https://github.com/carpyncho/carpyncho-py

```

To list all availables tiles you can run

``` console
$ carpyncho list-tiles
- b206
- b214
- b216
...
```

Then you can check the available catalogs for a given tile with

```console
$ carpyncho list-catalogs b216
Tile b216
    - features
    - lc
```

Lets asume we want to download the catalog *features* from the tile *b216*.
First lets check how big is the catalog before download:

```console
carpyncho catalog-info b216 features
Catalog b216-features
    - hname: Features
    - format: BZIP2-Parquet
    - extension: .parquet.bz2
    - date: 2020-04-14
    - md5sum: 433aae05541a2f5b191aa95d717fa83c  features_b216.parquet.bz2
    - filename: features_b216.parquet.bz2
    - driveid: 1-t165sLjn0k507SFeW-A4p9wYVL9rP4B
    - size: 142.2 MiB
    - records: 334,773
```

Well `142 MiB` for `334773` rows in the table, lets download it and sotore
it in `csv` format

```console
$ carpyncho download-catalog b216 features --out b216_features.csv
b216-features:   100%|█████████████████████████████| 149M/149M [02:15, 1.10Mb/s]
Writing b216_features.csv...
```

Now lets check the size and the checksum to see if it's correct
(warning this is linux and mac only)

```console
$ cat b216_features.csv | wc
334774

```

The rows are ok, so it's done.

## Contact

For bugs or question please contact

> **Juan B. Cabral:** [jbcabral@unc.edu.ar](jbcabral@unc.edu.ar)
