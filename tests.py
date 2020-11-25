#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2020, Juan B Cabral
# License: BSD-3-Clause
#   Full Text: https://github.com/carpyncho/carpyncho-py/blob/master/LICENSE


# =============================================================================
# DOCS
# =============================================================================

"""Integration Test for carpyncho.

Warning this code is SLOW!

"""


# =============================================================================
# IMPORTS
# =============================================================================

import atexit
import os
import pathlib
import shutil
import tempfile
import uuid

import carpyncho

import humanize

import numpy as np

import pandas as pd

import pytest


# =============================================================================
# CONSTANTS
# =============================================================================

PATH = pathlib.Path(os.path.abspath(os.path.dirname(__file__)))

LOCAL_INDEX = str(PATH / "data" / "index.json")

TEST_CACHE_PATH = tempfile.mkdtemp(suffix="_carpyncho_test")

atexit.register(shutil.rmtree, TEST_CACHE_PATH)


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def client_maker(mocker):
    def maker(**kwargs):
        tuid = str(uuid.uuid1())
        cache_dir = os.path.join(TEST_CACHE_PATH, tuid)
        mocker.patch("carpyncho.DEFAULT_CACHE_DIR", cache_dir)
        client = carpyncho.Carpyncho(**kwargs)
        client.cache.clear()
        return client

    return maker


@pytest.fixture
def client(client_maker):
    return client_maker(index_url=LOCAL_INDEX)


@pytest.fixture
def remote_client(client_maker):
    return client_maker(index_url=carpyncho.CARPYNCHO_INDEX_URL)


# =============================================================================
# CLIENT TEST
# =============================================================================


def test_index(client):
    index = client.retrieve_index(reset=True)
    assert client.index_ == index


def test_list_tiles(client):
    index = client.retrieve_index(reset=True)
    keys = {k for k in index.keys() if not k.startswith("_")}
    assert set(client.list_tiles()) == keys


def test_list_catalogs(client):
    index = client.retrieve_index(reset=True)
    for tile_name, tile_data in index.items():
        ftypes = set(tile_data)
        assert set(client.list_catalogs(tile_name)) == ftypes

    with pytest.raises(ValueError):
        client.list_catalogs("foo")


def test_has_catalog(client):
    index = client.retrieve_index(reset=True)
    for tile_name, tile_data in index.items():
        for cat in tile_data.keys():
            assert client.has_catalog(tile_name, cat)
            assert not client.has_catalog(tile_name, "foo")
    assert not client.has_catalog("foo", "foo")


def test_catalog_info(client):
    index = client.retrieve_index(reset=True)
    for tile_name, tile_data in index.items():
        for cat, cat_data in tile_data.items():
            assert client.catalog_info(tile_name, cat) == cat_data

            with pytest.raises(ValueError):
                client.catalog_info(tile_name, "foo")

    with pytest.raises(ValueError):
        client.catalog_info("foo", "foo")


def test_get_catalog(client):
    df = client.get_catalog("_test", "parquet_bz2_small")
    assert isinstance(df, pd.DataFrame)


# =============================================================================
# CLI TEST
# =============================================================================


def test_CLI_list_tiles(client, script_runner):
    expected = "\n".join(f"  - {t}" for t in client.list_tiles())
    ret = script_runner.run("carpyncho", "list-tiles")
    assert ret.stdout.strip() == expected.strip()
    assert ret.stderr == ""


def test_CLI_list_catalogs(client, script_runner):
    expected = "Tile '_test'\n" + "\n".join(
        f"  - {c}" for c in client.list_catalogs("_test")
    )
    ret = script_runner.run("carpyncho", "list-catalogs", "_test")
    assert ret.stdout.strip() == expected.strip()
    assert ret.stderr == ""


def test_CLI_has_catalog(client, script_runner):
    ret = script_runner.run(
        "carpyncho", "has-catalog", "_test", "parquet_bz2_small"
    )
    assert ret.stdout.strip().endswith(": exists")
    assert ret.stderr == ""

    ret = script_runner.run("carpyncho", "has-catalog", "_test", "nope")
    assert ret.stdout.strip().endswith(": NO exists")
    assert ret.stderr == ""


def test_CLI_catalog_info(client, script_runner):
    tile, catalog = "_test", "parquet_bz2_small"
    info = client.catalog_info(tile, catalog)

    size = humanize.naturalsize(info["size"], binary=True)
    records = humanize.intcomma(info["records"])

    expected = "\n".join(
        [
            f"Catalog {tile}-{catalog}",
            f"  - hname: {info['hname']}",
            f"  - format: {info['format']}",
            f"  - extension: {info['extension']}",
            f"  - date: {info['date']}",
            f"  - md5sum: {info['md5sum']}",
            f"  - filename: {info['filename']}",
            f"  - driveid: {info['driveid']}",
            f"  - size: {size}",
            f"  - records: {records}",
        ]
    )

    ret = script_runner.run("carpyncho", "catalog-info", tile, catalog)

    assert ret.stdout.strip() == expected.strip()
    assert ret.stderr == ""


def test_CLI_download_catalog(client, script_runner):
    outpath = os.path.join(TEST_CACHE_PATH, "test.csv")

    ret = script_runner.run(
        "carpyncho",
        "download-catalog",
        "_test",
        "parquet_bz2_small",
        "--out",
        outpath,
    )
    assert ret.stdout.strip() == f"Writing {outpath}..."
    assert "_test-parquet_bz2_small: " in ret.stderr


# =============================================================================
# INDEX JSON TEST
# =============================================================================


def test_parse_local_index(client):
    schema = {
        "hname": str,
        "format": str,
        "extension": str,
        "date": str,
        "md5sum": str,
        "filename": str,
        "driveid": str,
        "size": int,
        "records": int,
    }
    index = client.retrieve_index(reset=True)
    for tile, tdata in index.items():
        for cat, cdata in tdata.items():
            for k, v in cdata.items():
                assert k in schema
                assert isinstance(v, schema[k])
    assert index == client.index_


def test_parse_remote_index(remote_client):
    schema = {
        "hname": str,
        "format": str,
        "extension": str,
        "date": str,
        "md5sum": str,
        "filename": str,
        "driveid": str,
        "size": int,
        "records": int,
    }
    index = remote_client.retrieve_index(reset=True)
    for tile, tdata in index.items():
        for cat, cdata in tdata.items():
            for k, v in cdata.items():
                assert k in schema
                assert isinstance(v, schema[k])
    assert index == remote_client.index_


# =============================================================================
# TEST ENGINES
# =============================================================================


def test_parquet_engines(client_maker):
    clients = [
        client_maker(index_url=LOCAL_INDEX),
        client_maker(index_url=LOCAL_INDEX, parquet_engine="auto"),
        client_maker(index_url=LOCAL_INDEX, parquet_engine="pyarrow"),
        client_maker(index_url=LOCAL_INDEX, parquet_engine="fastparquet"),
    ]

    results = [
        client.get_catalog("_test", "parquet_bz2_small") for client in clients
    ]

    checks = [np.all(results[0] == rst) for rst in results[1:]]
    assert np.all(checks)


def test_CLI_parquet_engines(client, script_runner):

    results = []
    for engine in ["auto", "pyarrow", "fastparquet"]:
        outpath = os.path.join(TEST_CACHE_PATH, f"test_{engine}.csv")
        script_runner.run(
            "carpyncho",
            "download-catalog",
            "_test",
            "parquet_bz2_small",
            "--out",
            outpath,
            "--parquet-engine",
            engine,
            "--force",
        )
        results.append(pd.read_csv(outpath))

    checks = [np.all(results[0] == rst) for rst in results[1:]]
    assert np.all(checks)
