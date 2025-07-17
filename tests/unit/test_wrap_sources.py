# -*- coding: utf-8 -*-

# Copyright (C) 2024 Red Hat, Inc.
# Author: Tomas Jelinek <tojeline@redhat.com>
# SPDX-License-Identifier: MIT

# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

# Helper functions in this module cannot be typed easily and no benefit would
# come from it. They are called from typed context, so we silent untyped_calls.
# mypy: disallow_untyped_calls=False

from contextlib import contextmanager
from typing import Generator
from unittest import TestCase

from .ha_cluster_info import exporter_package

wrap_src = exporter_package.wrap_src

DESC = "Desc"


def _wrap(data):  # type: ignore
    # pylint: disable=protected-access
    return wrap_src._wrap_src(data, wrap_src._Context(data, DESC))


def _access_path(data, path):  # type: ignore
    for key in path:
        data = data[key]
    return data


class TestWrapSources(TestCase):
    # pylint: disable=protected-access
    # Checks without need to assign (testing exceptions), so:
    # pylint: disable=expression-not-assigned, pointless-statement
    # pylint: disable=too-many-public-methods

    def assert_wrap_eq(self, data, path):  # type: ignore
        self.assertEqual(
            _access_path(data, path),
            wrap_src._cleanup_wrap(_access_path(_wrap(data), path)),
        )

    @contextmanager
    def assert_invalid_src(  # type: ignore
        self,
        data,
        issue_location: str = "",
        issue_desc: str = "",
    ) -> Generator:
        with self.assertRaises(wrap_src.InvalidSrc) as e:
            yield
        self.assertEqual(
            e.exception.kwargs,
            dict(
                data=data,
                data_desc=DESC,
                issue_location=issue_location,
                issue_desc=issue_desc,
            ),
        )

    def check_scalar_key_access(self, data) -> None:  # type: ignore
        data_type = type(data).__name__
        with self.assert_invalid_src(
            data,
            issue_desc=(f"Expected dict with key 'a' but got '{data_type}'"),
        ):
            _wrap(data)["a"]

        with self.assert_invalid_src(
            data,
            issue_desc=(f"Expected dict with key 'a' but got '{data_type}'"),
        ):
            "a" in _wrap(data)

    def check_scalar_not_iterable(self, data) -> None:  # type: ignore
        data_type = type(data).__name__
        with self.assert_invalid_src(
            data,
            issue_desc=(f"Expected iterable but got '{data_type}'"),
        ):
            for _item in _wrap(data):
                pass

    def check_scalar_not_keys_items_values(self, data) -> None:  # type: ignore
        data_type = type(data).__name__
        with self.assert_invalid_src(
            data,
            issue_desc=(f"Expected dict but got '{data_type}'"),
        ):
            _wrap(data).keys()
        with self.assert_invalid_src(
            data,
            issue_desc=(f"Expected dict but got '{data_type}'"),
        ):
            _wrap(data).values()
        with self.assert_invalid_src(
            data,
            issue_desc=(f"Expected dict but got '{data_type}'"),
        ):
            _wrap(data).items()

    def test_dict_successful_access(self) -> None:
        data = {
            "a": {"b": "c"},
            "d": ["e", "f"],
            "g": "abc",
            "h": 1,
            "i": 1.2,
            "j": True,
            "k": None,
        }
        self.assert_wrap_eq(data, ["a", "b"])
        self.assert_wrap_eq(data, ["d", 1])
        self.assert_wrap_eq(data, ["g"])
        self.assert_wrap_eq(data, ["h"])
        self.assert_wrap_eq(data, ["i"])
        self.assert_wrap_eq(data, ["j"])
        self.assert_wrap_eq(data, ["k"])

    def test_dict_missing_key(self) -> None:
        data = {"a": 1}
        with self.assert_invalid_src(data, issue_desc="Missing key 'b'"):
            _wrap(data)["b"]

    def test_dict_index_access(self) -> None:
        data = {"a": 1}
        with self.assert_invalid_src(
            data,
            issue_desc="Expected list with index '0' but got 'dict'",
        ):
            _wrap(data)[0]

    def test_dict_no_sliceable(self) -> None:
        data = {"a": 1}

        with self.assert_invalid_src(
            data,
            issue_desc=("Invalid access by 'slice(None, -1, None)' to 'dict'"),
        ):
            _wrap(data)[:-1]

    def test_dict_keys_protected(self) -> None:
        # we have a dict instead of list of dicts...
        data = {"outer": {"some_key": 1}}
        with self.assert_invalid_src(
            data,
            # it's a little bit cryptic but rare case - good enough
            issue_desc="Expected dict with key 'x' but got 'str'",
            issue_location="/outer",
        ):
            for item in _wrap(data)["outer"]:
                item["x"]  # item is str "some_key" now
        # pylint: disable=consider-iterating-dictionary
        self.assertEqual(
            [key.unwrap() for key in _wrap({"a": 1, "b": 2}).keys()], ["a", "b"]
        )

    def test_dict_values_wrapped(self) -> None:
        self.assertEqual(
            [key.unwrap() for key in _wrap({"a": 1, "b": 2}).values()], [1, 2]
        )

    def test_dict_items_wrapped(self) -> None:
        self.assertEqual(
            [
                (key.unwrap(), value.unwrap())
                for key, value in _wrap({"a": 1, "b": 2}).items()
            ],
            [("a", 1), ("b", 2)],
        )

    def test_dict_accept_wrapped_keys(self) -> None:
        # E.g. we take node name from one part and use it as key in another part
        self.assertEqual(_wrap({"a": 1})[_wrap("a")].unwrap(), 1)

    def test_list_key_access(self) -> None:
        data = [1]
        with self.assert_invalid_src(
            data,
            issue_desc="Expected dict with key 'a' but got 'list'",
        ):
            _wrap(data)["a"]

    def test_list_index_out_of_range(self) -> None:
        data = [1]
        with self.assert_invalid_src(
            data,
            issue_desc="Index '1' out of range",
        ):
            _wrap(data)[1]

    def test_list_iterate(self) -> None:
        data = [1, 3, 5]
        result = []
        for item in _wrap(data):
            result.append(item)
        self.assertEqual(result, data)

    def test_list_slice_works_correctly(self) -> None:
        self.assertEqual(_wrap(["a", "b", "c"])[:-1].unwrap(), ["a", "b"])

    def test_list_add_works_correctly(self) -> None:
        self.assertEqual(
            (_wrap(["a", "b", "c"]) + _wrap(["d"])).unwrap(),
            ["a", "b", "c", "d"],
        )

    def test_dict_accept_wrapped_indexes(self) -> None:
        self.assertEqual(_wrap(["a", "b"])[_wrap(1)].unwrap(), "b")

    def test_scalar_key_access(self) -> None:
        self.check_scalar_key_access(1)
        self.check_scalar_key_access(1.1)
        self.check_scalar_key_access(True)
        self.check_scalar_key_access(None)

    def test_scalar_no_iterable(self) -> None:
        self.check_scalar_not_iterable(1)
        self.check_scalar_not_iterable(1.1)
        self.check_scalar_not_iterable(True)
        self.check_scalar_not_iterable(None)

    def test_scalar_cannot_keys_items_values(self) -> None:
        self.check_scalar_not_keys_items_values(1)
        self.check_scalar_not_keys_items_values(1.1)
        self.check_scalar_not_keys_items_values(True)
        self.check_scalar_not_keys_items_values(1)
        self.check_scalar_not_keys_items_values("abc")
        self.check_scalar_not_keys_items_values([1, 2])

    def no_test_scalar_no_sliceable(self) -> None:
        # Unfortunately, python does not call __getitem__ when trying use slice
        # on descendant of int but there is some kind of shortcut :(
        data = 1

        with self.assert_invalid_src(
            data,
            issue_desc=("'int' object is not subscriptable"),
        ):
            _wrap(data)[:-1]

    def test_string_key_access(self) -> None:
        data = {"a": "abc"}
        with self.assert_invalid_src(
            data,
            issue_location="/a",
            issue_desc="Expected dict with key 'a' but got 'str'",
        ):
            _wrap(data)["a"]["a"]

    def test_string_instead_of_list_of_objects(self) -> None:
        data = {"obj": "abc"}
        with self.assert_invalid_src(
            data,
            issue_desc=("Expected dict with key 'x' but got 'str'"),
            issue_location="/obj/0",
        ):
            for obj in _wrap(data)["obj"]:
                obj["x"]

        with self.assert_invalid_src(
            data,
            issue_desc=("Expected dict with key 'x' but got 'str'"),
            issue_location="/obj/0",
        ):
            for obj in _wrap(data)["obj"][:]:
                obj["x"]

    def test_string_slice_works_correctly(self) -> None:
        self.assertEqual(_wrap("abc")[:-1].unwrap(), "ab")

    def test_string_add_works_correctly(self) -> None:
        self.assertEqual((_wrap("abc") + _wrap("d")).unwrap(), "abcd")

    def test_none_sorting(self) -> None:
        data = {"a": [1, 2, None]}
        with self.assert_invalid_src(
            data,
            issue_desc=(
                "Comparison not supported between 'NoneType' and 'int'"
            ),
            issue_location="/a/2",
        ):
            sorted(_wrap(data)["a"])

    def test_none_compare(self) -> None:
        data = {"a": None, "b": "some"}
        self.assertTrue(wrap_src.is_none(None))
        self.assertTrue(wrap_src.is_none(_wrap(data)["a"]))
        self.assertFalse(wrap_src.is_none("some"))
        self.assertFalse(wrap_src.is_none(_wrap(data)["b"]))

    def test_bool_comparison(self) -> None:
        data = {"a": True}
        with self.assert_invalid_src(
            data,
            issue_desc=(
                "Unsupported operand type(s) for 'xor': 'bool' and 'str'"
            ),
            issue_location="/a",
        ):
            _wrap(data)["a"] ^ "a"

    def test_can_run_other_invalid_src_exception(self) -> None:
        data = {"a": {"b": "invalid"}}
        with self.assert_invalid_src(
            data,
            issue_desc=("Ad hoc err"),
            issue_location="/a/b",
        ):
            raise wrap_src.invalid_part(_wrap(data)["a"]["b"], "Ad hoc err")
