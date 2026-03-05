#!/usr/bin/env python
import sys

import pytest

sys.path.append("xypath")
import tcore

import xypath


class TestJunctionMissing(tcore.TMissing):
    def test_cell_missing(self):
        a = self.table.filter("2").assert_one()
        b = self.table.filter("4").assert_one()
        junction_result = list(a.junction(b))
        assert len(junction_result) == 0


class TestJunction(tcore.TCore):
    def test_cell_junction(self):
        a = self.table.filter("WORLD").assert_one()
        b = self.table.filter("1990-1995").assert_one()
        junction_result = list(a.junction(b))
        assert 1 == len(junction_result)
        (x, y, z) = junction_result[0]
        assert isinstance(x, xypath.Bag)
        assert isinstance(y, xypath.Bag)
        assert isinstance(z, xypath.Bag)
        assert "WORLD" == x.value
        assert "1990-1995" == y.value
        assert 1.523 == z.value

    def test_bag_junction(self):
        a = self.table.filter("WORLD")
        b = self.table.filter("1990-1995")
        j = list(a.junction(b))
        assert 1 == len(j)
        (a_result, b_result, value_result) = j[0]
        assert 1.523 == value_result.value

    def test_bag_junction_checks_type(self):
        bag = self.table.filter("Estimates")
        with pytest.raises(TypeError):
            list(bag.junction("wrong_type"))

    def test_junction_raises(self):
        a = self.table.filter("WORLD")
        b = self.table.filter("AFRICA")  # is below WORLD
        with pytest.raises(xypath.JunctionError):
            list(a.junction(b))

    def test_waffle(self):
        a = self.table.filter("WORLD")
        b = self.table.filter("1990-1995")
        j = a.waffle(b, direction=(0, 1), paranoid=True)
        assert isinstance(j, xypath.Bag)
        assert 1 == len(j)
        for item in j:
            assert 1.523 == item.value
