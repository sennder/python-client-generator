import typing as t

from contextlib import contextmanager


@contextmanager
def does_not_raise() -> t.Generator:
    yield
