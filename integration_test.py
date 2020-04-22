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
# EQUATORIAL TESTCASE
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
    assert set(client.list_tiles()) == set(index.keys())


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
    df = client.get_catalog("_test", "small")
    assert isinstance(df, pd.DataFrame)
