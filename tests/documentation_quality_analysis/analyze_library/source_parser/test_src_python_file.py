import pandas.core.indexes.base as base


def _func1_coerce_method(converter):
    pass


class Class1_NDFrame:
    def __init__(self):
        a = "some init code here"


class class_2_Series(base.IndexOpsMixin, Class1_NDFrame):
    def __init__(self,
                 data="some data",
                 index=None,
                 dtype: None = None,
                 name=None,
                 copy: bool | None = None,
                 fastpath: bool = False) -> None:
        super().__init__()
        return

    def func1_in_series(self, a, b, c, e=1, f=2) -> str:
        return "some value"

    def func2_in_series(self):
        return


def func2_ravel(self, x, y, order: str = "C") -> list:
    pass
