#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2020, Juan B Cabral
# License: BSD-3-Clause
#   Full Text: https://github.com/carpyncho/carpyncho-py/blob/master/LICENSE


# =============================================================================
# DOCS
# =============================================================================

"""Python client for Carpyncho VVV dataset collection.

This code access as a Pandas DataFrame all the data of the web version of
Carpyncho https://carpyncho.github.io/.

"""


__all__ = ["Carpyncho", "CARPYNCHOPY_DATA_PATH"]


__version__ = "0.0.6"


# =============================================================================
# IMPORTS
# =============================================================================

import os
import io
import bz2
import pathlib
import typing as t
import inspect
import hashlib
import functools
import urllib
import json

import attr

import diskcache as dcache

import tqdm

import humanize

import requests

import clize

import pandas as pd


# =============================================================================
# CONSTANTS
# =============================================================================

VERSION = __version__

#: Location of the entire dataset index.
CARPYNCHO_INDEX_URL = "https://raw.githubusercontent.com/carpyncho/carpyncho-py/master/data/index.json"  # noqa

#: Google drive location.
DRIVE_URL = "https://docs.google.com/uc?export=download"


#: Where carpyncho gonna store the entire data.
CARPYNCHOPY_DATA_PATH = pathlib.Path(
    os.path.expanduser(os.path.join('~', 'carpyncho_py_data')))


#: Chunk size when the library are download the big files of Carpyncho.
CHUNK_SIZE = 32768

#: Maximun cache size (10TB)
DEFAULT_CACHE_SIZE_LIMIT = int(1e10)

#: The location of the cache catabase and files.
DEFAULT_CACHE_DIR = CARPYNCHOPY_DATA_PATH / "_cache_"

#: The default carpyncho parquet default
DEFAULT_PARQUET_ENGINE = "auto"


# =============================================================================
# CACHE ORCHESTRATION
# =============================================================================

def from_cache(
    cache, tag, function, cache_expire,
    force=False, *args, **kwargs
):
    """Simplify cache orchestration.

    Parameters
    ----------
    tag: str
        Normally every function call the cache with their own tag.
        We sugest "module.function" or "module.Class.function"

    function: callable
        The function to be cached

    force: bool (default=False)
        If the vale of the cache must be ignored and re-execute the
        function.

    cache_expire: bool or None
        Time in seconds to expire the function call

    args and kwargs:
        All the parameters needed to execute the function.

    Returns
    -------
    The result of calling the function or the cached version of the same value.

    """
    # start the cache orchestration
    key = dcache.core.args_to_key(
        base=("carpyncho", tag), args=args, kwargs=kwargs, typed=False)

    with cache as c:
        c.expire()

        value = (
            dcache.core.ENOVAL if force else
            c.get(key, default=dcache.core.ENOVAL, retry=True))

        if value is dcache.core.ENOVAL:
            value = function(**kwargs)
            c.set(
                key, value, expire=cache_expire,
                tag=f"carpyncho.{tag}", retry=True)

    return value


# =============================================================================
# CLIENT
# =============================================================================

@attr.s(hash=False, frozen=True)
class Carpyncho:
    """Client to access the *Carpyncho VVV dataset collection*.

    This code access as a Pandas Dataframe all the data of the web version of
    Carpyncho. https://carpyncho.github.io/.

    Parameters
    ----------
    cache : ``diskcache.Cache``, ``diskcache.Fanout``,
        or ``None`` (default: ``None``)
        Any instance of ``diskcache.Cache``, ``diskcache.Fanout`` or
        ``None`` (Default). If it's ``None`` a ``diskcache.Cache``
        istance is created with the parameter
        ``directory = carpyncho.DEFAULT_CACHE_DIR``.
        More information: http://www.grantjenks.com/docs/diskcache
    cache_expire : ``float`` or None (default=``None``)
        Seconds until item expires (default ``None``, no expiry)
        More information: http://www.grantjenks.com/docs/diskcache
    parquet_engine : ``str`` (default="auto")
        Default Parquet library to use.
        Remotely carpyncho stores all the data as compresses parquet files;
        When the download happend a this must be parsed.
        If ‘auto’, then the option io.parquet.engine is used.
        The default io.parquet.engine behavior is to try ‘pyarrow’, falling
        back to ‘fastparquet’ if ‘pyarrow’ is unavailable.


    """

    #: Local cache of the carpyncho database.
    cache: t.Union[dcache.Cache, dcache.FanoutCache] = attr.ib()

    #: Default timout of the catalog-cache.
    #: Try to always set to None (default), the catalogs are big and mostly
    #: never change.
    cache_expire: float = attr.ib(default=None, repr=False)

    #: Default Parquet library to use.
    parquet_engine: str = attr.ib(DEFAULT_PARQUET_ENGINE)

    #: Location of the carpyncho index (usefull for development)
    index_url: str = attr.ib(default=CARPYNCHO_INDEX_URL)

    # =========================================================================
    # ATTRS ORCHESTRATION
    # =========================================================================

    @cache.default
    def _cache_default(self):
        return dcache.Cache(
            directory=DEFAULT_CACHE_DIR, size_limit=DEFAULT_CACHE_SIZE_LIMIT)

    # =========================================================================
    # UTILITIES FOR CHECK THE REMOTE DATA
    # =========================================================================

    def retrieve_index(self, reset):
        """Access the remote index of the Carpyncho-Dataset.

        The index is stored internally for 1 hr.

        Parameters
        ----------
        reset: bool
            If its True the entire cache is ignored and a new index is
            donwloaded and cached.

        Returns
        -------
        dict with the index structure.

        """
        def get_json_data(url):
            parsed = urllib.parse.urlparse(url)
            if parsed.scheme in ("http", "https", "ftp"):
                response = requests.get(
                    url, headers={'Cache-Control': 'no-cache'})
                return response.json()
            with open(url) as fp:
                return json.load(fp)

        return from_cache(
            cache=self.cache,
            tag="get_index",
            function=get_json_data,
            cache_expire=3600,
            force=reset,
            url=self.index_url)

    @property
    def index_(self):
        """Structure of the Carpyncho dataset information as a Python-dict."""
        return self.retrieve_index(reset=False)

    def list_tiles(self):
        """Retrieve available tiles with catalogs as a tuple of str."""
        index = self.index_
        return tuple(k for k in index.keys() if not k.startswith("_"))

    def list_catalogs(self, tile):
        """Retrieve the available catalogs for a given tile.

        Parameters
        ----------
        tile: str
            The name of the tile to retrieve the catalogs.

        Returns
        -------
        tuple of str:
            The names of available catalogs in the given tile.

        Raises
        ------
        ValueError:
            If the tile is not found.

        """
        index = self.index_
        if tile not in index:
            raise ValueError(f"Tile {tile} not found")
        return tuple(index[tile])

    def has_catalog(self, tile, catalog):
        """Check if a given catalog and tile exists.

        Parameters
        ----------
        tile: str
            The name of the tile.
        catalog:
            The name of the catalog.

        Returns
        -------
        bool:
            True if the convination tile+catalog exists.

        """
        cat = self.index_.get(tile, {}).get(catalog)
        return bool(cat)

    def catalog_info(self, tile, catalog):
        """Retrieve the information about a given catalog.

        Parameters
        ----------
        tile: str
            The name of the tile.
        catalog:
            The name of the catalog.

        Returns
        -------
        dict:
            The entire information of the given catalog file. This include
            drive-id, md5 checksum, size in bytes, number of total records,
            etc.

        Raises
        ------
        ValueError:
            If the tile or the catalog is not found.

        """
        index = self.index_

        if tile not in index:
            raise ValueError(f"Tile {tile} not found")

        tile = index[tile]
        if catalog not in tile:
            raise ValueError(
                f"Catalog {catalog} for tile {tile} not found")

        return tile[catalog]

    # =========================================================================
    # THE DOWNLOAD PART
    # =========================================================================

    def _grive_download(self, tile, catalog, driveid, size, md5sum):

        # https://stackoverflow.com/a/39225272
        # https://stackoverflow.com/a/27508615

        # prepare the parameters and download the token
        params = {'id': driveid}
        session = requests.Session()
        response = session.get(
            DRIVE_URL, params=params, stream=True,
            headers={'Cache-Control': 'no-cache'})

        # retrieve the token from gdrive page
        token = None
        for key, value in response.cookies.items():
            if key.startswith('download_warning'):
                token = value
                break

        # if we have token add to the parameters
        if token:
            params['confirm'] = token

        # make the real deal request
        response = session.get(
            DRIVE_URL, params=params, stream=True,
            headers={'Cache-Control': 'no-cache'})

        # progress bar
        pbar = tqdm.tqdm(
            total=size, initial=0, unit='B',
            unit_scale=True, desc=f"{tile}-{catalog}")

        # the file is a bz2 file, we are going to decompress and store
        # the raw parquet data into a BytesIO
        decompressor = bz2.BZ2Decompressor()
        parquet_stream = io.BytesIO()

        # ademas necesitamos fijarnos que el md5 este ok
        file_hash = hashlib.md5()

        # retrive all the data one chunk at the time
        for chunk in response.iter_content(CHUNK_SIZE):
            if not chunk:
                break
            parquet_stream.write(decompressor.decompress(chunk))
            file_hash.update(chunk)
            pbar.update(CHUNK_SIZE)

        # stop the progress bar
        pbar.close()

        # check if the file was download correctly
        if file_hash.hexdigest() != md5sum:
            raise IOError(
                f"'{tile}-{catalog}' incorrect download.\n"
                f"expected: {md5sum}\n"
                f"caclulated: {file_hash.hexdigest()}")

        # read the entire stream into a dataframe
        parquet_stream.seek(0)
        df = pd.read_parquet(parquet_stream, engine=self.parquet_engine)
        return df

    def get_catalog(self, tile, catalog, force=False):
        """Retrieve a catalog from the carpyncho dataset.

        Parameters
        ----------
        tile: str
            The name of the tile.
        catalog:
            The name of the catalog.
        force: bool (default=False)
            If its True, the cached version of the catalog is ignored and
            redownloaded. Try to always set force to False.

        Returns
        -------
        pandas.DataFrame:
            The columns of the DataFrame changes between the different catalog.

        Raises
        ------
        ValueError:
            If the tile or the catalog is not found.
        IOError:
            If the checksum not match.

        """
        info = self.catalog_info(tile, catalog)
        driveid, size = info["driveid"], info["size"]
        md5sum = info["md5sum"].split()[0].strip().lower()

        df = from_cache(
            cache=self.cache,
            tag="get_catalog",
            function=self._grive_download,
            cache_expire=self.cache_expire,
            force=force,

            # params to _gdrive_download
            tile=tile, catalog=catalog,
            driveid=driveid, size=size, md5sum=md5sum)

        return df


# =============================================================================
# CLI
# =============================================================================

class CLI:
    """Carpyncho console client.

    Explore and download the entire https://carpyncho.github.io/
    catalogs from your command line.

    """

    footnotes = "\n".join([
        "This software is under the BSD 3-Clause License.",
        "Copyright (c) 2020, Juan Cabral.",
        "For bug reporting or other instructions please check:"
        " https://github.com/carpyncho/carpyncho-py"])

    def get_commands(self):
        methods = {}
        for k in dir(self):
            if k.startswith("_"):
                continue
            v = getattr(self, k)
            if inspect.ismethod(v) and k != "get_commands":
                methods[k] = v
        return methods

    def version(self):
        """Print Carpyncho version."""
        print(VERSION)

    def list_tiles(self):
        """Show available tiles."""
        client = Carpyncho()
        for tile in client.list_tiles():
            print(f"- {tile}")

    def list_catalogs(self, tile):
        """Show the available catalogs for a given tile.

        tile:
            The name of the tile to retrieve the catalogs.

        """
        client = Carpyncho()
        print(f"Tile {tile}")
        for catalog in client.list_catalogs(tile=tile):
            print(f"    - {catalog}")

    def has_catalog(self, tile, catalog):
        """Check if a given catalog and tile exists.

        tile:

        catalog:
            The name of the catalog.

        """
        client = Carpyncho()
        has = "" if client.has_catalog(tile, catalog) else "NO "
        print(f"Catalog '{catalog}' or tile '{tile}': {has}exists")

    def catalog_info(self, tile, catalog):
        """Retrieve the information about a given catalog.

        tile:
            The name of the tile.

        catalog:
            The name of the catalog.

        """
        FORMATTERS = {
            "size": functools.partial(humanize.naturalsize, binary=True),
            "records": humanize.intcomma
        }

        client = Carpyncho()
        print(f"Catalog {tile}-{catalog}")
        for k, v in client.catalog_info(tile, catalog).items():
            fmt = FORMATTERS.get(k, str)
            print(f"    - {k}: {fmt(v)}")

    def download_catalog(
        self, tile, catalog,
        *, force=False, parquet_engine=DEFAULT_PARQUET_ENGINE, out
    ):
        """Retrives a catalog from th Carpyncho dataset collection.

        tile:
            The name of the tile.

        catalog:
            The name of the catalog.

        out:
            Path to store the catalog. The extension of the file detemines
            the format. Options are ".xlsx" (Excel), ".csv",
            ".pkl" (Python pickle) and ".parquet".

        force:
            Force to ignore the cached value and redownload the catalog.
            Try to always set force to False.

        parquet_engine:
            Parquet engine to decode.

        """
        PARSERS = {
            ".xlsx": pd.DataFrame.to_excel,
            ".csv": pd.DataFrame.to_csv,
            ".pkl": pd.DataFrame.to_pickle,
            ".parquet": pd.DataFrame.to_parquet}

        client = Carpyncho(parquet_engine=parquet_engine)

        df = client.get_catalog(tile, catalog, force=force)

        ext = os.path.splitext(out)[-1].lower()
        if ext not in PARSERS:
            raise clize.UserError(f"format '{ext}' not recognized")

        print(f"Writing {out}...")
        parser = PARSERS[ext]
        parser(df, out)


def main():
    """Run the carpyncho CLI interface."""
    cli = CLI()
    commands = tuple(cli.get_commands().values())
    clize.run(
        *commands,
        description=cli.__doc__,
        footnotes=cli.footnotes)


if __name__ == "__main__":
    main()
