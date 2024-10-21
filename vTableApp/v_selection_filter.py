from contextlib import contextmanager

import numpy as np
import pandas as pd

from .v_autocomplete import Autocomplete


class SelectionFilter(Autocomplete):
    def __init__(self, values, *, callbacks=None, label=""):
        super().__init__(
            v_model=[],
            label=label,
        )
        self.callbacks = None
        self._values = None
        self.values = values
        self.observe(self._invoke_callbacks, names="v_model")
        self.callbacks = callbacks

    @property
    def values(self):
        return self.items

    @values.setter
    def values(self, values):
        if isinstance(values, pd.Series) and isinstance(
            values.dtype, pd.CategoricalDtype
        ):
            unique_values = np.asarray(values.dtype.categories)
        else:
            unique_values = np.unique(values)
        self.items = unique_values.tolist()

    @property
    def value(self):
        return tuple(self.v_model)

    @value.setter
    def value(self, value):
        value = [_value for _value in value if _value in self.values]
        value = tuple(value)
        if value == self.value:
            return
        super().v_model = list(value)

    def reset(self):
        self.value = []

    @contextmanager
    def block_callbacks(self):
        _callbacks = self.callbacks
        self.callbacks = None
        try:
            yield
        except Exception as e:
            raise e
        finally:
            self.callbacks = _callbacks

    def _invoke_callbacks(self, *args):
        if self.callbacks is None:
            return
        for callback in self.callbacks:
            callback(("selected_values", self.value))
