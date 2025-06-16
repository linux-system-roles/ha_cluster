# -*- coding: utf-8 -*-

# Copyright (C) 2024 Red Hat, Inc.
# Author: Tomas Jelinek <tojeline@redhat.com>
# SPDX-License-Identifier: MIT

"""
This module addresses the following issue:
When exporting the current cluster configuration, configuration data is loaded
from various sources, and the cluster configuration is built from this source
data in the appropriate format. If the source data does not conform to the
expected format (e.g., a missing key, a string instead of an object), an
exception is raised. However, source data can be quite extensive and nested,
making it difficult to locate the issue based on the brief information from
built-in exceptions.

To resolve this, a set of wrappers is introduced for every Python type that
can be obtained from JSON format (i.e., str, int, float, dict, list, bool,
None). Non-JSON sources are loaded into JSON-compatible types. These wrappers
track the current position within the source data and propagate this
information if an exception needs to be raised.

Since it's necessary to work with elements (e.g., normalizing a string with
`.lower()`), the wrappers must support all operations the wrapped type can
perform. However, the interface of these types is extensive. Therefore, where
possible, wrapper classes inherit directly from the type they wrap. In such
cases, the wrapped data is stored in two places: in the `_data` attribute and
passed to the constructor of the built-in type. Where inheritance from a
built-in type is not possible (e.g., Python does not allow inheriting from
`bool`), a different approach is applied.

Wrapper classes also provide methods to detect and report misuse of a
particular type. This allows for handling the most common unmet expectations
(e.g., when an integer is provided where a dictionary is expected, and an
attempt is made to iterate over it).

Non-scalar types are wrapped entirely, and their individual parts are wrapped
lazily, on demand.

This module does not cover situations where, for example, a string is expected
but a dictionary is found instead, and the caller unwittingly uses this
"expected" string directly in the output.
"""

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
    # For compatibility with older Python versions
    SupportsIndex = Any  # type: ignore


SrcDict = Dict[str, Any]
Scalar = Union[bool, int, float, None]
CleanSrc = Union[dict, list, str, Scalar]
Path = Optional[List[Union[str, int]]]
Func = Callable[..., CleanSrc]
ItemAccess = Union[str, SupportsIndex, slice]


class InvalidSrc(Exception):
    """Raised when JSON source data cannot be interpreted as expected."""

    def __init__(
        self,
        data_desc: str,
        data: SrcDict,
        issue_location: str,
        issue_desc: str,
    ):
        self.data = data  # Original source dictionary
        self.data_desc = data_desc  # Description for the user
        self.issue_location = issue_location  # Path within the JSON
        self.issue_desc = issue_desc  # What went wrong

    @property
    def kwargs(self) -> Dict[str, Any]:
        """Original arguments passed to this exception."""
        return dict(
            data=self.data,
            data_desc=self.data_desc,
            issue_location=self.issue_location,
            issue_desc=self.issue_desc,
        )


def wrap_src_for_rich_report(
    params_to_wrap: Dict[str, str],
) -> Callable[[Func], Func]:
    """
    Decorator factory to automatically wrap specified parameters
    with rich-context-aware wrappers (_WrapSrc family).

    The idea is to wrap every element in JSON sources with an object containing
    the element's context, catch common cases of invalid sources, and provide
    helpful error messages to the user to identify where a discrepancy between
    the expected and the actual source structure lies.

    params_to_wrap -- Dict: Names of parameters that should be wrapped as the
        keys and its description for use in error messages as the values.
    """

    def decorator(func: Func) -> Func:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> CleanSrc:
            sig = signature(func)
            # We don't know the interface of decorated function so, we must
            # deduce it from signature.
            # This fills the parameters of the decorated function with the
            # values with which the decorated function was called.
            # Method `bind` returns a dict: keys are argument names from
            # signature of the decorated function and values are values passed
            # to the decorated function.
            bound = sig.bind(*args, **kwargs)
            # For args not provided, use their default values. Just be complete.
            bound.apply_defaults()
            for param, desc in params_to_wrap.items():
                if param in bound.arguments:
                    # Wrap arguments mentioned in `param_names`
                    bound.arguments[param] = _wrap_src(
                        bound.arguments[param],
                        _Context(bound.arguments[param], desc),
                    )
            return _cleanup_wrap(func(*bound.args, **bound.kwargs))

        return wrapper

    return decorator


class _Context:
    """
    Holds contextual metadata to produce informative exceptions when extraction
    fails.
    """

    def __init__(self, src: SrcDict, desc: str, path: Path = None) -> None:
        """
        src -- original source
        desc -- description of the original source
        path -- path within nested structures, accumulates keys/indices
        """
        self._src = src
        self._desc = desc
        self._path = path if path is not None else []

    def invalid_src(self, issue_desc: str) -> InvalidSrc:
        """Constructs an InvalidSrc for a given problem description."""
        return InvalidSrc(
            self._desc,
            self._src,
            f"/{'/'.join(str(p) for p in self._path)}" if self._path else "",
            issue_desc,
        )

    def wrap(self, data: Any, key: Union[str, int] = "") -> "_WrapSrc":
        """Wrap a nested piece of data, extending the path with `key`."""
        context = _Context(
            self._src, self._desc, self._path + ([key] if key != "" else [])
        )
        return _wrap_src(data, context)


class _WrapSrc:
    """Abstract base for all wrappers"""

    _data: CleanSrc
    _context: _Context

    def __init__(self, data: CleanSrc, context: _Context) -> None:
        self._data = data
        self._context = context

    @property
    def _type(self) -> str:
        return type(self._data).__name__  # e.g. 'dict', 'list', 'int'

    def _invalid_src(self, issue_desc: str) -> InvalidSrc:
        return self._context.invalid_src(issue_desc)

    def _index_out_of_range(self, index: SupportsIndex) -> InvalidSrc:
        return self._invalid_src(f"Index '{index}' out of range")

    def _expected_dict(self, key: Optional[str] = None) -> InvalidSrc:
        key_desc = f" with key '{key}'" if key else ""
        return self._invalid_src(
            f"Expected dict{key_desc} but got '{self._type}'"
        )

    def _expected_list(self, key: int) -> InvalidSrc:
        return self._invalid_src(
            f"Expected list with index '{key}' but got '{self._type}'"
        )

    def _invalid_access(self, i: ItemAccess) -> InvalidSrc:
        return self._invalid_src(f"Invalid access by '{i}' to '{self._type}'")

    def _unsupported_access(self, key: ItemAccess) -> InvalidSrc:
        if isinstance(key, _WrapSrc):
            key = key.unwrap()

        if isinstance(key, str):
            return self._expected_dict(key)

        if isinstance(key, int):
            # Dict can be indexed by int as well but not in JSON.
            return self._expected_list(key)

        return self._invalid_access(key)

    def _wrap(self, data: Any, key: Union[str, int] = "") -> "_WrapSrc":
        return self._context.wrap(data, key)

    def unwrap(self) -> Any:
        """Returns the original, unwrapped data."""
        return self._data

    def invalid_part(self, reason: str) -> InvalidSrc:
        """Returns an exception indicating that this specific part is invalid."""
        return self._invalid_src(reason)


class _WrapScalar(_WrapSrc):
    """
    Abstract base for scalar types (bool, int, float, None).

    Methods report attempts to use scalar types as str, list or dict.
    """

    _data: Scalar

    def __getitem__(self, key: ItemAccess) -> _WrapSrc:
        raise self._unsupported_access(key)

    def __contains__(self, key: Union[str, int]) -> bool:
        raise self._unsupported_access(key)

    def __iter__(self) -> Iterator:
        raise self._invalid_src(f"Expected iterable but got '{self._type}'")

    def keys(self) -> _WrapSrc:  # pylint: disable=missing-function-docstring
        raise self._expected_dict()

    def values(self) -> _WrapSrc:  # pylint: disable=missing-function-docstring
        raise self._expected_dict()

    def items(self) -> _WrapSrc:  # pylint: disable=missing-function-docstring
        raise self._expected_dict()


class _WrapInt(int, _WrapScalar):
    _data: int

    def __new__(cls, data: int, context: _Context) -> "_WrapInt":
        # __new__ because int is immutable and __init__ is called post-create.
        instance = super().__new__(cls, data)
        _WrapSrc.__init__(instance, data, context)
        return instance


class _WrapFloat(float, _WrapScalar):
    _data: float

    def __new__(cls, data: float, context: _Context) -> "_WrapFloat":
        # __new__ because float is immutable and __init__ is called post-create.
        instance = super().__new__(cls, data)
        _WrapSrc.__init__(instance, data, context)
        return instance


class _WrapBool(int, _WrapScalar):
    # Cannot inherit from bool but can emulate its interface.. Try it in shell.
    # See: https://mail.python.org/pipermail/python-dev/2002-March/020822.html
    # And: https://peps.python.org/pep-0285/
    # This class adds improved error reporting => it makes sense to extend bool
    _data: bool

    def __new__(cls, data: bool, context: _Context) -> "_WrapBool":
        # __new__ because int is immutable and __init__ is called post-create.
        instance = super().__new__(cls, bool(data))
        _WrapSrc.__init__(instance, data, context)
        return instance

    def __repr__(self) -> str:
        # Provide a clearer repr than the inherited int(bool) repr
        return f"<WrappedJsonBool {bool(self)!r}>"

    def __bool__(self) -> bool:
        return bool(int(self))

    def _safe_cmp(self, op: Any, other: object, reverse: bool = False) -> bool:
        # Method encapsulates common handling for comparison.
        if isinstance(other, _WrapSrc):
            # The comparison can be with another wrapped src.
            other = other.unwrap()
        try:
            # For right operand - reverse
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


class _WrapNone(_WrapScalar):
    # Cannot inherit from None (similar to bool), so its interface is emulated.
    _data: None

    def __init__(self, context: Any) -> None:
        # Only context matters; data is always None
        super().__init__(None, context)

    def _safe_cmp(self, op: Any, other: object) -> bool:
        # Method encapsulates common handling for comparison.
        if isinstance(other, _WrapSrc):
            # The comparison can be with another wrapped source.
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
        # None equals only None or another WrapNone
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
    """
    Abstract base for sequence types (list and str).

    Methods report attempts to use list/string types as a dict.
    """

    _data: Union[list, str]

    def _get_item(
        self,
        get_item: Callable[[Any], Any],
        index: ItemAccess,
    ) -> Any:
        # Deduplicates __getitem__ logic for both lists and strings.

        if isinstance(index, self.__class__):
            index = index.unwrap()

        if isinstance(index, str):
            # Reject string index and report attempt to use list/str as dict.
            raise self._expected_dict(index)

        if isinstance(index, slice):
            # Return wrapped subsequence for slicing
            return self._wrap(get_item(index))

        try:
            return self._wrap(get_item(index), int(index))
        except IndexError as e:
            raise self._index_out_of_range(index) from e

    def _iter(self) -> Iterator:
        # Yield wrapped elements with their indices
        return (self._wrap(v, i) for i, v in enumerate(self._data))

    def _add(self, other: Any) -> Any:
        if isinstance(other, self.__class__):
            other = other.unwrap()
        # Support concatenation for lists and strings
        return self._wrap(self._data + other)

    def keys(self) -> _WrapSrc:  # pylint: disable=missing-function-docstring
        raise self._expected_dict()

    def values(self) -> _WrapSrc:  # pylint: disable=missing-function-docstring
        raise self._expected_dict()

    def items(self) -> _WrapSrc:  # pylint: disable=missing-function-docstring
        raise self._expected_dict()


class _WrapStr(str, _WrapSeq):
    _data: str

    def __new__(cls, data: str, context: _Context) -> "_WrapStr":
        # __new__ because str is immutable and __init__ is called post-create.
        instance = super().__new__(cls, data)
        _WrapSrc.__init__(instance, data, context)
        return instance

    def __getitem__(self, index: ItemAccess) -> str:
        return self._get_item(super().__getitem__, index)

    def __iter__(self) -> Iterator:
        return self._iter()

    def __add__(self, other: Any) -> "_WrapStr":
        return self._add(other)


class _WrapList(list, _WrapSeq):
    _data: list

    def __init__(self, data: list, context: _Context) -> None:
        super().__init__(data)
        _WrapSrc.__init__(self, data, context)

    def __getitem__(self, index: ItemAccess) -> Any:
        return self._get_item(super().__getitem__, index)

    def __iter__(self) -> Iterator:
        return self._iter()

    def __add__(self, other: Any) -> "_WrapList":
        return self._add(other)


class _WrapDict(dict, _WrapSrc):
    _data: dict

    def __init__(self, data: dict, context: _Context) -> None:
        super().__init__(data)
        _WrapSrc.__init__(self, data, context)

    def __getitem__(self, key: ItemAccess) -> _WrapSrc:
        if isinstance(key, _WrapSrc):
            # Key could be gained from src (e.g. node name) and thus wrapped.
            key = key.unwrap()

        if not isinstance(key, str):
            # Only string keys allowed for a dict representing a JSON object.
            raise self._unsupported_access(key)

        try:
            return self._wrap(self._data[key], key)
        except KeyError as e:
            raise self._invalid_src(f"Missing key '{key}'") from e

    def __iter__(self) -> Iterator:
        # Why wrap keys? If we have this dict but expected a list of dicts,
        # and call something like `key["key_of_expected_dict"]`, we wouldn't get
        # an InvalidSrc with an unwrapped key.
        return (self._wrap(key) for key in iter(self._data))

    def get(self, key: str, default: Any = None) -> Any:
        """Overrides dict's get method."""
        if key in self._data:
            return self._wrap(self._data[key], key)
        # Do not wrap! Inappropriate use of this does not mean an invalid src.
        # The src is actually the caller itself.
        return default

    # We don't need the reflection of dict changes provided by dict views since
    # we don't plan to change the sources. Let's use a simpler Iterator here.
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
    for data_type, wrapper in wrap_map.items():
        if isinstance(data, data_type):
            return wrapper(data, context)

    return _WrapNone(context)


def _cleanup_wrap(maybe_wrapped: Union[CleanSrc, _WrapSrc]) -> CleanSrc:
    """Recursively unwraps any wrapped values into pure Python types."""
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


def invalid_part(data: Union[_WrapSrc, CleanSrc], reason: str) -> Exception:
    """
    Returns an exception indicating that the wrapped data was detected as
    invalid, even though it has the correct structure.
    """
    if not isinstance(data, _WrapSrc):
        # This should not happen...
        return TypeError(reason)
    return data.invalid_part(reason)


def is_none(maybe_none: Union[CleanSrc, _WrapSrc]) -> bool:
    """
    Returns True if the `maybe_none` value represents None.

    Unfortunately, Python does not provide a way to capture `is None` within
    any `__*__` method.
    """
    if isinstance(maybe_none, _WrapSrc):
        maybe_none = maybe_none.unwrap()
    return maybe_none is None
