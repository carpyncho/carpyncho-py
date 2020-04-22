#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2020, Juan B Cabral
# License: BSD-3-Clause
#   Full Text: https://github.com/carpyncho/carpyncho-py/blob/master/LICENSE


# =============================================================================
# DOCS
# =============================================================================

"""Python client for Carpyncho VVV Data collection
(https://carpyncho.github.io/)

Esta libreria descarga y transforma los datos para una utilización más
comoda.


"""


__all__ = ["Carpyncho", "CARPYNCHOPY_DATA_PATH"]


__version__ = "0.0.1b"


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

import attr

import diskcache as dcache

import tqdm

import requests

import clize

import pandas as pd


# =============================================================================
# CONSTANTS
# =============================================================================

CARPYNCHO_INDEX_URL = "https://raw.githubusercontent.com/carpyncho/carpyncho-py/master/data/index.json"  # noqa

DRIVE_URL = "https://docs.google.com/uc?export=download"

CARPYNCHOPY_DATA_PATH = pathlib.Path(
    os.path.expanduser(os.path.join('~', 'carpyncho_py_data')))

CHUNK_SIZE = 32768

DEFAULT_CACHE_DIR = CARPYNCHOPY_DATA_PATH / "_cache_"


# =============================================================================
# CACHE ORCHESTRATION
# =============================================================================

def from_cache(
    cache, tag, function, cache_expire,
    force=False, *args, **kwargs
):
    """Simple cache orchestration.

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
    """Client to access the *Carpyncho VVV Data collection*
    (https://carpyncho.github.io/)

    Parameters
    ----------

    url : ``str`` (default: ``carpyncho.URL``)
        The endpoint of the carpyncho index file.
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

    """

    cache: t.Union[dcache.Cache, dcache.FanoutCache] = attr.ib()
    cache_expire: float = attr.ib(default=3600, repr=False)

    # =========================================================================
    # ATTRS ORCHESTRATION
    # =========================================================================

    @cache.default
    def _cache_default(self):
        return dcache.Cache(directory=DEFAULT_CACHE_DIR)

    # =========================================================================
    # UTILITIES FOR CHECK THE REMOTE DATA
    # =========================================================================

    def retrieve_index(self, reset):
        def get_and_json(url):
            return requests.get(url).json()

        return from_cache(
            cache=self.cache,
            tag="get_index",
            function=get_and_json,
            cache_expire=3600,
            force=reset,
            url=CARPYNCHO_INDEX_URL)

    @property
    def index_(self):
        return self.retrieve_index(reset=False)

    def list_tiles(self):
        index = self.index_
        return tuple(k for k in index.keys() if not k.startswith("_"))

    def list_catalogs(self, tile):
        index = self.index_
        if tile not in index:
            raise ValueError(f"Tile {tile} not found")
        return tuple(index[tile])

    def has_catalog(self, tile, catalog):
        cat = self.index_.get(tile, {}).get(catalog)
        return bool(cat)

    def catalog_info(self, tile, catalog):
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
        response = session.get(DRIVE_URL, params=params, stream=True)

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
        response = session.get(DRIVE_URL, params=params, stream=True)

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
        df = pd.read_parquet(parquet_stream)
        return df

    def get_catalog(self, tile, catalog):
        info = self.catalog_info(tile, catalog)
        driveid, size = info["driveid"], info["size"]
        md5sum = info["md5sum"].split()[0].strip().lower()

        df = from_cache(
            cache=self.cache,
            tag="get_catalog",
            function=self._grive_download,
            cache_expire=None,
            force=False,

            # params to _gdrive_download
            tile=tile, catalog=catalog,
            driveid=driveid, size=size, md5sum=md5sum)

        return df


# =============================================================================
# CLI
# =============================================================================

@attr.s(hash=False, frozen=True)
class CLI:
    """Carpyncho console client.

    This file can explore the entire https://carpyncho.github.io/
    catalogs from your command line.

    """

    client = attr.ib()

    def get_methods(self):
        methods = {}
        for k in dir(self):
            if k.startswith("_"):
                continue
            v = getattr(self, k)
            if inspect.ismethod(v) and v is not self.get_methods:
                methods[k] = v
        return methods

    def list_tiles(self):
        for tile in self.client.list_tiles():
            print(f"- {tile}")

    def list_catalogs(self, tile):
        print(f"Tile {tile}")
        for catalog in self.client.list_catalogs(tile=tile):
            print(f"    - {catalog}")

    def has_catalog(self, tile, catalog):
        has = "" if self.client.has_catalog(tile, catalog) else "NO "
        print(f"Catalog '{catalog}' or tile '{tile}': {has}exists")

    def catalog_info(self, tile, catalog):
        print(f"Catalog {tile}-{catalog}")
        for k, v in self.client.catalog_info(tile, catalog).items():
            if k == "size":
                new_v = v / 1024 / 1024
                unit = "MiB"
                if new_v < 1:
                    new_v = v / 1024
                    unit = "KiB"
                if new_v < 1:
                    new_v = v
                    unit = "B"
                v = f"{new_v:.2f} {unit}"
            print(f"    - {k}: {v}")

    def get_catalog(self, tile, catalog, *, out):
        PARSERS = {
            ".xlsx": pd.DataFrame.to_excel,
            ".csv": pd.DataFrame.to_csv,
            ".pkl": pd.DataFrame.to_pickle,
            ".parquet": pd.DataFrame.to_parquet}

        df = self.client.get_catalog(tile, catalog)

        ext = os.path.splitext(out)[-1].lower()
        if ext not in PARSERS:
            raise clize.UserError(f"format '{ext}' not recognized")

        print(f"Writing {out}...")
        parser = PARSERS[ext]
        parser(df, out)


def main():
    cli = CLI(client=Carpyncho())
    commands = tuple(cli.get_methods().values())
    clize.run(*commands)


if __name__ == "__main__":
    main()
