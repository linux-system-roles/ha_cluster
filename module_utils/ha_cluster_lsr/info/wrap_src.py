# -*- coding: utf-8 -*-

# Copyright (C) 2024 Red Hat, Inc.
# Author: Tomas Jelinek <tojeline@redhat.com>
# SPDX-License-Identifier: MIT

# make ansible-test happy, even though the module requires Python 3
from __future__ import absolute_import, division, print_function

# make ansible-test happy, even though the module requires Python 3
# pylint: disable=invalid-name
__metaclass__ = type

import functools
import operator
from inspect import signature
from typing import (
    Any,
    Callable,
    Dict,
    Iterator,
    List,
    Optional,
    Union,
)

try:
    from typing import SupportsIndex
except ImportError:
    SupportsIndex = Union[int, Any]  # type: ignore


SrcDict = Dict[str, Any]
Scalar = Union[bool, int, float, None]
CleanSrc = Union[dict, list, str, Scalar]
Path = Optional[List[Union[str, int]]]
Func = Callable[..., CleanSrc]
ItemAccess = Union[str, SupportsIndex, slice]


class InvalidSrc(Exception):
    """Cannot extract result from sources"""

    def __init__(
        self,
        data_desc: str,
        data: SrcDict,
        issue_location: str,
        issue_desc: str,
    ):
        self.data = data
        self.data_desc = data_desc
        self.issue_location = issue_location
        self.issue_desc = issue_desc

    @property
    def kwargs(self) -> Dict[str, Any]:
        """Arguments given to the constructor"""
        return dict(
            data=self.data,
            data_desc=self.data_desc,
            issue_location=self.issue_location,
            issue_desc=self.issue_desc,
        )


def wrap_src_for_rich_report(
    *param_names: str, data_desc: str
) -> Callable[[Func], Func]:
    """
    Decorator to wrap specified parameters as _WrapSrc objects.

    The idea is to wrap every element in JSON sources with object containing
    context, catch common cases of invalid sources and provide to a user helpful
    error messages to identify where a discrepancy between the expected and the
    actual source structure is.

    param_names -- Names of parameters that should be wrapped.
    data_desc -- Description of the data for use in error messages.
    """

    def decorator(func: Func) -> Func:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> CleanSrc:
            sig = signature(func)
            # Combine function signature and given arguments. Get dict: keys are
            # argument names and values are values passed to wrapper.
            bound = sig.bind(*args, **kwargs)
            # For not given arguments use it's default values. Just be complete.
            bound.apply_defaults()
            for param in param_names:
                if param in bound.arguments:
                    # Wrap agruments mentioned as `param_names`
                    bound.arguments[param] = _wrap_src(
                        bound.arguments[param],
                        _Context(bound.arguments[param], data_desc),
                    )
            return _cleanup_wrap(func(*bound.args, **bound.kwargs))

        return wrapper

    return decorator


class _Context:
    def __init__(self, src: SrcDict, desc: str, path: Path = None) -> None:
        self._src = src
        self._desc = desc
        self._path = path if path is not None else []

    def invalid_src(self, issue_desc: str) -> Exception:
        """Returns InvalidSrc exception"""
        return InvalidSrc(
            self._desc,
            self._src,
            f"/{'/'.join(str(p) for p in self._path)}" if self._path else "",
            issue_desc,
        )

    def wrap(self, data: Any, key: Union[str, int] = "") -> Any:
        """Returns a wraped source part bound to this context"""
        context = _Context(
            self._src, self._desc, self._path + ([key] if key != "" else [])
        )
        return _wrap_src(data, context)


class _WrapSrc:  # pylint: disable=too-few-public-methods
    """Base class for all wrappers"""

    _data: CleanSrc
    _context: _Context

    def __init__(self, data: CleanSrc, context: _Context) -> None:
        self._data = data
        self._context = context

    @property
    def _type(self) -> str:
        return type(self._data).__name__

    def _invalid_src(self, issue_desc: str) -> Exception:
        return self._context.invalid_src(issue_desc)

    def _index_out_of_range(self, index: SupportsIndex) -> Exception:
        return self._invalid_src(f"Index '{index}' out of range")

    def _expected_dict(self, key: Optional[str] = None) -> Exception:
        key_desc = f" with key '{key}'" if key else ""
        return self._invalid_src(
            f"Expected dict{key_desc} but got '{self._type}'"
        )

    def _invalid_access(self, i: ItemAccess) -> Exception:
        return self._invalid_src(f"Invalid access by '{i}' to '{self._type}'")

    def _unsupported_access(self, key: ItemAccess) -> Exception:
        if isinstance(key, _WrapSrc):
            key = key.unwrap()

        if isinstance(key, str):
            return self._expected_dict(key)

        if isinstance(key, int):
            return self._invalid_src(
                f"Expected list with index '{key}' but got '{self._type}'",
            )

        return self._invalid_access(key)

    def _wrap(self, data: Any, key: Union[str, int] = "") -> Any:
        return self._context.wrap(data, key)

    def unwrap(self) -> Any:
        """Returns the original, unwrapped data."""
        return self._data


class _WrapScalar(_WrapSrc):
    _data: Scalar

    def __getitem__(self, key: ItemAccess) -> Any:
        raise self._unsupported_access(key)

    def __contains__(self, key: Union[str, int]) -> bool:
        raise self._unsupported_access(key)

    def __iter__(self) -> Iterator:
        raise self._invalid_src(f"Expected iterable but got '{self._type}'")

    def keys(self) -> Any:  # pylint: disable=missing-function-docstring
        raise self._expected_dict()

    def values(self) -> Any:  # pylint: disable=missing-function-docstring
        raise self._expected_dict()

    def items(self) -> Any:  # pylint: disable=missing-function-docstring
        raise self._expected_dict()


class _WrapInt(int, _WrapScalar):
    _data: int

    def __new__(cls, data: int, context: _Context) -> "_WrapInt":
        instance = super().__new__(cls, data)
        _WrapSrc.__init__(instance, data, context)
        return instance


class _WrapFloat(float, _WrapScalar):
    _data: float

    def __new__(cls, data: float, context: _Context) -> "_WrapFloat":
        instance = super().__new__(cls, data)
        _WrapSrc.__init__(instance, data, context)
        return instance


class _WrapBool(int, _WrapScalar):  # Cannot inherit form bool
    _data: bool

    def __new__(cls, data: bool, context: _Context) -> "_WrapBool":
        instance = super().__new__(cls, bool(data))
        _WrapSrc.__init__(instance, data, context)
        return instance

    def __repr__(self) -> str:
        return f"<WrappedJsonBool {bool(self)!r}>"

    def __bool__(self) -> bool:
        return bool(int(self))

    def _safe_cmp(self, op: Any, other: object, reverse: bool = False) -> bool:
        if isinstance(other, _WrapSrc):
            other = other.unwrap()
        try:
            return op(other, bool(self)) if reverse else op(bool(self), other)
        except TypeError as e:
            raise self._invalid_src(
                f"Unsupported operand type(s) for '{op.__name__}': 'bool'"
                f" and '{type(other).__name__}'"
            ) from e

    def __and__(self, other: int) -> int:
        return self._safe_cmp(operator.and_, other)

    def __or__(self, other: int) -> int:
        return self._safe_cmp(operator.or_, other)

    def __xor__(self, other: int) -> int:
        return self._safe_cmp(operator.xor, other)

    def __invert__(self) -> bool:
        return not bool(self)

    def __rand__(self, other: int) -> int:
        return self._safe_cmp(operator.and_, other, reverse=True)

    def __ror__(self, other: int) -> int:
        return self._safe_cmp(operator.or_, other, reverse=True)

    def __rxor__(self, other: int) -> int:
        return self._safe_cmp(operator.xor, other, reverse=True)


class _WrapNone(_WrapScalar):  # Cannot inherit from None
    _data: None

    def __init__(self, context: Any) -> None:
        super().__init__(None, context)

    def _safe_cmp(self, op: Any, other: object) -> bool:
        if isinstance(other, _WrapSrc):
            other = other.unwrap()
        try:
            return op(None, other)
        except TypeError as e:
            raise self._invalid_src(
                "Comparison not supported between 'NoneType'"
                f" and '{type(other).__name__}'"
            ) from e

    def __bool__(self) -> bool:
        return False

    def __eq__(self, other: object) -> bool:
        return other is None or isinstance(other, _WrapNone)

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __lt__(self, other: object) -> bool:
        return self._safe_cmp(operator.lt, other)

    def __le__(self, other: object) -> bool:
        return self._safe_cmp(operator.le, other)

    def __gt__(self, other: object) -> bool:
        return self._safe_cmp(operator.gt, other)

    def __ge__(self, other: object) -> bool:
        return self._safe_cmp(operator.ge, other)

    def __hash__(self) -> int:
        return hash(None)

    def __repr__(self) -> str:
        return "<WrapNone>"


class _WrapSeq(_WrapSrc):
    _data: Union[list, str]

    def _get_item(
        self,
        get_item: Callable[[Any], Any],
        index: ItemAccess,
    ) -> Any:
        if isinstance(index, self.__class__):
            index = index.unwrap()

        if isinstance(index, str):
            raise self._expected_dict(index)

        if isinstance(index, slice):
            return self._wrap(get_item(index))

        try:
            return self._wrap(get_item(index), int(index))
        except IndexError as e:
            raise self._index_out_of_range(index) from e

    def _iter(self) -> Iterator:
        return (self._wrap(v, i) for i, v in enumerate(self._data))

    def keys(self) -> Any:  # pylint: disable=missing-function-docstring
        raise self._expected_dict()

    def values(self) -> Any:  # pylint: disable=missing-function-docstring
        raise self._expected_dict()

    def items(self) -> Any:  # pylint: disable=missing-function-docstring
        raise self._expected_dict()


class _WrapStr(str, _WrapSeq):
    _data: str

    def __new__(cls, data: str, context: _Context) -> "_WrapStr":
        instance = super().__new__(cls, data)
        _WrapSrc.__init__(instance, data, context)
        return instance

    def __getitem__(self, index: ItemAccess) -> str:
        return self._get_item(super().__getitem__, index)

    def __iter__(self) -> Iterator:
        return self._iter()


class _WrapList(list, _WrapSeq):
    _data: list

    def __init__(self, data: list, context: _Context) -> None:
        super().__init__(data)
        _WrapSrc.__init__(self, data, context)

    def __getitem__(self, index: ItemAccess) -> Any:
        return self._get_item(super().__getitem__, index)

    def __iter__(self) -> Iterator:
        return self._iter()


class _WrapDict(dict, _WrapSrc):
    _data: dict

    def __init__(self, data: dict, context: _Context) -> None:
        super().__init__(data)
        _WrapSrc.__init__(self, data, context)

    def __getitem__(self, key: ItemAccess) -> Any:
        if isinstance(key, _WrapSrc):
            key = key.unwrap()

        if not isinstance(key, str):
            raise self._unsupported_access(key)

        try:
            return self._wrap(self._data[key], key)
        except KeyError as e:
            raise self._invalid_src(f"Missing key '{key}'") from e

    def __iter__(self) -> Iterator:
        # Why wrap keys? We can access keys as objects, when we got dict where
        # we expect e.g. list of dict.
        return (self._wrap(key) for key in iter(self._data))

    def get(self, key: str, default: Any = None) -> Any:
        """Overwrites dict's get"""
        if key in self._data:
            return self._wrap(self._data[key], key)
        # Don't wrap! Inappropriate use of this does not mean invalid source.
        return default

    # We don't appreciate reflection of the dict change provided by dict view
    # since we don't plan change sources. Let's use simpler Iterator here.
    def keys(self) -> Iterator:  # type: ignore[override]
        return (self._wrap(key) for key in self._data.keys())

    def values(self) -> Iterator:  # type: ignore[override]
        return (self._wrap(value) for value in self._data.values())

    def items(self) -> Iterator:  # type: ignore[override]
        return (
            (self._wrap(key), self._wrap(value))
            for key, value in self._data.items()
        )


def _wrap_src(data: CleanSrc, context: _Context) -> _WrapSrc:
    # In JSON, values must be one of the following data types:
    # a string -> str
    # a number -> int|float
    # an object (JSON object) -> dict, keys are strings
    # an array -> list
    # a boolean -> bool
    # null -> None
    wrap_map = {
        str: _WrapStr,
        bool: _WrapBool,  # bool before int since bool extends int!
        int: _WrapInt,
        float: _WrapFloat,
        list: _WrapList,
        dict: _WrapDict,
    }
    for data_type, wraper in wrap_map.items():
        if isinstance(data, data_type):
            return wraper(data, context)

    return _WrapNone(context)


def _cleanup_wrap(maybe_wrapped: Union[CleanSrc, _WrapSrc]) -> CleanSrc:
    top_clean = (
        maybe_wrapped.unwrap()
        if isinstance(maybe_wrapped, _WrapSrc)
        else maybe_wrapped
    )

    if isinstance(top_clean, dict):
        return {
            _cleanup_wrap(key): _cleanup_wrap(value)
            for key, value in top_clean.items()
        }

    if isinstance(top_clean, list):
        return [_cleanup_wrap(item) for item in top_clean]

    return top_clean
