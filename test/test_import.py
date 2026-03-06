#!/usr/bin/env python
import sys

import pytest

sys.path.append("xypath")

import xypath

try:
    import hamcrest
except ImportError:
    hamcrest = None
import tcore


class Test_Import_Missing(tcore.TMissing):
    def test_table_has_properties_at_all(self):
        self.table.sheet


class Test_Import(tcore.TCore):
    def test_table_has_sheet_properties(self):
        assert self.table.sheet is not None
        assert hasattr(self.table.sheet, "name")

    # import
    def test_from_filename_with_table_name(self):
        """Can we specify only the filename and 'name' of the table?"""
        if hamcrest is None:
            pytest.skip("Requires Hamcrest")
        table = xypath.Table.from_filename(self.wpp_filename, table_name="NOTES")
        assert 32 == len(table)
        table.filter(hamcrest.contains_string("(2) Including Zanzibar.")).assert_one()

    # import
    def test_from_filename_with_table_index(self):
        """Can we specify only the filename and index of the table?"""
        new_table = xypath.Table.from_filename(self.wpp_filename, table_index=5)
        assert 1 == len(new_table.filter("(2) Including Zanzibar."))

    # import
    def test_from_file_object_table_index(self):
        with open(self.wpp_filename, "rb") as f:
            extension = tcore.get_extension(self.wpp_filename)
            new_table = xypath.Table.from_file_object(f, extension, table_index=5)
        assert 1 == len(new_table.filter("(2) Including Zanzibar."))

    # import
    def test_from_file_object_table_name(self):
        with open(self.wpp_filename, "rb") as f:
            extension = tcore.get_extension(self.wpp_filename)
            new_table = xypath.Table.from_file_object(f, extension, table_name="NOTES")
        assert 1 == len(new_table.filter("(2) Including Zanzibar."))

    # import
    def test_from_file_object_no_table_specifier(self):
        with open(self.wpp_filename, "rb") as f:
            extension = tcore.get_extension(self.wpp_filename)
            with pytest.raises(TypeError):
                xypath.Table.from_file_object(f, extension)

    # import
    def test_from_file_object_ambiguous_table_specifier(self):
        with open(self.wpp_filename, "rb") as f:
            extension = tcore.get_extension(self.wpp_filename)

            with pytest.raises(TypeError):
                xypath.Table.from_file_object(
                    f, extension, table_name="NOTES", table_index=4
                )

    # import
    def test_from_messy(self):
        new_table = xypath.Table.from_messy(self.messy.tables[0])
        assert 265 == len(new_table.filter("Estimates"))

    def test_xlsx_uses_openpyxl_sheet(self):
        table = xypath.Table.from_filename(
            tcore.get_fixture_filename("acled.xlsx"), table_index=0
        )
        assert "openpyxl" in repr(table.sheet)
