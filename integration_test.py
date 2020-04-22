#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2020, Juan B Cabral
# License: BSD-3-Clause
#   Full Text: https://github.com/carpyncho/carpyncho-py/blob/master/LICENSE


# =============================================================================
# DOCS
# =============================================================================

"""Integration Test for carpyncho)

Warning this code is SLOW!

"""


# =============================================================================
# IMPORTS
# =============================================================================

import pytest

import pandas as pd

import carpyncho


# =============================================================================
# CLIENT TEST
# =============================================================================

@pytest.fixture
def client():
    client = carpyncho.Carpyncho()
    client.cache.clear()
    return client


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
    expected = "\n".join(
        f"- {t}" for t in client.list_tiles())
    ret = script_runner.run('carpyncho', "list-tiles")
    assert ret.stdout.strip() == expected
    assert ret.stderr == ''


def test_CLI_list_catalogs(client, script_runner):
    expected = (
        f"Tile _test\n" + "\n".join(
            f"    - {c}" for c in client.list_catalogs("_test")))
    ret = script_runner.run('carpyncho', "list-catalogs", "_test")
    assert ret.stdout.strip() == expected
    assert ret.stderr == ''


def test_CLI_has_catalog(client, script_runner):
    ret = script_runner.run(
        'carpyncho', "has-catalog", "_test", "parquet_bz2_small")
    assert ret.stdout.strip().endswith(": exists")
    assert ret.stderr == ''

    ret = script_runner.run(
        'carpyncho', "has-catalog", "_test", "nope")
    assert ret.stdout.strip().endswith(": NO exists")
    assert ret.stderr == ''


def test_CLI_catalog_info(client, script_runner):
    expected = "\n".join([
        "Catalog _test-parquet_bz2_small",
        "    - hname: Small parquet file",
        "    - format: BZIP2-Parquet",
        "    - extension: .parquet.bz2",
        "    - date: 2020-04-21",
        "    - md5sum: 10176f94027db8b636c9683a964cd8dc  small.parquet.bz2",
        "    - filename: small.parquet.bz2",
        "    - driveid: 1U_-8JMwnOLaXyDZp2_CgBX3WxxR7qnI4",
        "    - size: 2.96 KiB"])

    ret = script_runner.run(
        'carpyncho', "catalog-info", "_test", "parquet_bz2_small")

    assert ret.stdout.strip() == expected
    assert ret.stderr == ''


def test_CLI_get_catalog(client, script_runner):
    ret = script_runner.run(
        'carpyncho', "get-catalog",
        "_test", "parquet_bz2_small", "--out", "test.csv")
    assert ret.stdout.strip() == 'Writing test.csv...'
    assert "_test-parquet_bz2_small: " in ret.stderr
