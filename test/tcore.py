#!/usr/bin/env python
import collections
import collections.abc
import sys

import pytest

sys.path.append("xypath")
from os.path import abspath, dirname, splitext
from os.path import join as pjoin

for name in ("Mapping", "MutableMapping", "Sequence"):
    if not hasattr(collections, name):
        setattr(collections, name, getattr(collections.abc, name))

import messytables

import xypath

FIXTURE_DIR = pjoin(abspath(dirname(__file__)), "..", "fixtures")


def get_extension(filename):
    """
    >>> get_extension('/foo/bar/test.xls')
    'xls'
    """
    return splitext(filename)[1].strip(".")


def get_fixture_filename(name):
    return pjoin(FIXTURE_DIR, name)


def get_messytables_fixture(name, table_index=0, memoized={}):
    """
    Memoized function for loading fixtures
    """

    if name not in memoized:
        with open(name, "rb") as fd:
            extension = get_extension(name)
            messy = messytables.any.any_tableset(fd, extension=extension)
            messytable = messy.tables[table_index]
        memoized[name] = (messy, xypath.Table.from_messy(messytable))

    return memoized[name]


class TCore:
    @classmethod
    def setup_class(cls):
        cls.wpp_filename = get_fixture_filename("wpp.xls")
        cls.messy, cls.table = get_messytables_fixture(cls.wpp_filename)

    def setUp(self):
        pass

    # A special version of assertRaises() that tests both the
    # exception class, and the exception message. Based on:
    # http://stackoverflow.com/questions/8672754
    def assertRaisesWithMessage(self, func, exception_type, msg, *args, **kwargs):
        with pytest.raises(exception_type) as exc_info:
            func(*args, **kwargs)
        assert str(exc_info.value) == msg


class TMissing:
    @classmethod
    def setup_class(cls):
        cls.wpp_filename = get_fixture_filename("missingcell.csv")
        cls.messy, cls.table = get_messytables_fixture(cls.wpp_filename)

    def setUp(self):
        pass
