#!/usr/bin/env python
import sys

import pytest

sys.path.append("xypath")
import tcore

import xypath


class Test_Bag(tcore.TCore):
    def test_bag_from_list(self):
        "That Bag.from_list works and table is preserved"
        true_bag = self.table.filter(lambda b: b.x % 2 and b.y % 2)
        fake_bag = list(true_bag.table)
        assert isinstance(fake_bag, list)
        remade_bag = xypath.Bag.from_list(fake_bag)
        assert true_bag.table == remade_bag.table
        assert isinstance(remade_bag, xypath.Bag)
        assert len(remade_bag) == len(self.table)

    def test_bag_equality(self):
        lhs = self.table.filter("WORLD")
        rhs = self.table.filter("WORLD")

        assert lhs == rhs

        rhs = self.table.filter("Variant")

        assert lhs != rhs

    def test_bag_locations(self):
        world = self.table.filter("WORLD")
        empty = self.table.filter(lambda cell: False)

        assert world.excel_locations() == "C18"
        assert empty.excel_locations() == ""
        assert ", ..." in self.table.excel_locations()

    def test_bags_from_different_tables_are_not_equal(self):
        bag1 = self.table.filter(lambda b: True)
        bag2 = xypath.Table.from_bag(bag1)
        assert bag1 != bag2

    def test_corebag_iterator_size(self):
        """Test that the iterator yields as many results as len() claims"""
        bag = self.table.filter("Estimates")
        assert 265 == len(bag)
        assert len(bag) == len(list(bag))

    def test_corebag_iterator_nonduplicate(self):
        """
        Ensure that each call of CoreBag.__iter__ returns a new iterator

        Supercedes _test_corebag_iterator_size_squared
        """

        bag = self.table.filter("Estimates")
        assert iter(bag) is not iter(bag)

    def _test_corebag_iterator_size_squared(self):
        """Worry: that iterating twice over bag doesn't work property.
        Test: that every pair of cells from the bags is present."""
        bag = self.table.filter("Estimates")

        SIZE = 4
        # Limit bag size so that test isn't slow
        bag = bag.from_list([cell for cell in bag][:SIZE])

        n_bag = len(bag)
        assert n_bag == SIZE

        count = 0
        for i in bag:
            for j in bag:
                count = count + 1

        assert count == n_bag * n_bag

    def test_corebag_iterator_returns_bags(self):
        """Check the iterator returns bags, not _XYCells"""
        bag = self.table.filter("Estimates")
        for individual_cell in bag:
            assert isinstance(individual_cell, xypath.Bag)

    def test_singleton_bag_value(self):
        assert "Country code" == self.table.filter("Country code").value
        with pytest.raises(xypath.XYPathError):
            self.table.filter("Estimates").value

    def test_messytables_has_properties(self):
        for bag in self.table.unordered:
            bag.properties.get("jam")  # is vaguely dict-like

    def test_from_bag(self):
        world_pops_bag = self.table.filter(
            lambda b: b.y >= 16 and b.y <= 22 and b.x >= 5 and b.x <= 16
        )
        world_pops_table = xypath.Table.from_bag(world_pops_bag)

        # check extending the whole table gets lots of stuff all the way down
        fifties = self.table.filter("1950-1955")
        filties_col = fifties.fill(xypath.DOWN)
        assert 265 == len(filties_col)

        # check if we extend within the new world-only table, it only gets
        # stuff from the table
        fifties = world_pops_table.filter("1950-1955")
        filties_col = fifties.fill(xypath.DOWN)
        assert 6 == len(filties_col)

    def test_fill_down_without_termination(self):
        world_cell = self.table.filter("WORLD").assert_one()
        filled_down = world_cell.fill(xypath.DOWN)
        assert world_cell not in filled_down
        assert 264 == len(filled_down)

    def test_expand_down_without_termination(self):
        world_cell = self.table.filter("WORLD").assert_one()
        expand_down = world_cell.expand(xypath.DOWN)
        assert world_cell in expand_down
        assert 265 == len(expand_down)

    def test_fill_right_without_termination(self):
        world_cell = self.table.filter("WORLD").assert_one()
        filled_right = world_cell.fill(xypath.RIGHT)
        assert world_cell not in filled_right
        assert 14 == len(filled_right)

    def test_bag_intersection(self):
        bag = self.table.filter("Estimates")
        another_bag = self.table.filter("WORLD")
        union = bag | another_bag
        intersection = union & another_bag
        assert intersection.value == "WORLD"

    def test_bag_union(self):
        bag = self.table.filter("Estimates")
        another_bag = self.table.filter("WORLD")

        union = bag | another_bag
        assert len(bag) + len(another_bag) == len(union)

    def test_bag_set_difference(self):
        super_bag = self.table.filter("WORLD").assert_one().fill(xypath.DOWN)
        sub_bag = self.table.filter("AFRICA").assert_one()

        diff = super_bag - sub_bag

        assert len(super_bag) - len(sub_bag) == len(diff)

    def test_bag_set_difference_rhs_non_subset_of_lhs(self):
        super_bag = self.table.filter("WORLD").assert_one().fill(xypath.DOWN)
        unrelated_bag = self.table.filter("Estimates")

        diff = super_bag - unrelated_bag

        assert len(super_bag) == len(diff)
        assert super_bag == diff

    def test_bag_empty_is_ok(self):
        self.table.filter("BODGERANDBADGER").fill(xypath.RIGHT)

    def test_bag_ordering(self):

        # The purpose of this test is to have a "reasonably pathological" bag
        # so that the sort test is meaningful

        col1 = self.table.filter("Index").fill(xypath.DOWN)
        col2 = self.table.filter("Variant").fill(xypath.DOWN)

        bag = col1 | col2

        assert [1.0, "Estimates", 2.0, "Estimates"] == [
            cell.value for cell in list(bag)[:4]
        ]

        def yx(cell):
            return (cell.y, cell.x)

        assert sorted(bag, key=yx) == list(bag)

    def test_assert_one_with_zero(self):
        bag = self.table.filter("No Such Cell")
        with pytest.raises(AssertionError):
            bag.assert_one()
        with pytest.raises(xypath.NoCellsAssertionError):
            bag.assert_one()

    def test_assert_one_with_multiple(self):
        bag = self.table.filter("Estimates")
        with pytest.raises(AssertionError):
            bag.assert_one()
        with pytest.raises(xypath.MultipleCellsAssertionError):
            bag.assert_one()

    def test_table_rows(self):
        counter = 0
        rows = list(self.table.rows())
        for row in rows:
            counter = counter + len(row)
        assert len(self.table) == counter  # misses none
        assert len(rows) == 282

    def test_table_cols(self):
        counter = 0
        cols = list(self.table.cols())
        for col in cols:
            counter = counter + len(col)
        assert len(self.table) == counter  # misses none
        assert len(cols) == 17

    def test_has_table(self):
        assert isinstance(self.table, xypath.Table)
        assert isinstance(self.table, xypath.Bag)

    def test_select_other(self):
        pytest.skip("select_other not tested")

    def test_getattr(self):
        assert self.table.filter("WORLD").is_bold()
        assert not self.table.filter("WORLD").is_not_bold()
        assert self.table.filter("WORLD").font_name_is("Arial")
        assert not self.table.filter("WORLD").font_name_is_not("Arial")
        assert self.table.filter("WORLD").font_name_is_not("Comic Sans MS")
