from contextlib import contextmanager

import numpy as np

from .v_autocomplete import Autocomplete


class SelectionFilter(Autocomplete):
    def __init__(
        self, values, *, callbacks=None, label="", class_="ma-0 pa-0", style_=""
    ):
        super().__init__(
            selection=[],
            label=label,
            class_=class_,
            style_=style_,
        )
        self.callbacks = None
        self._values = None
        self.values = values
        self.observe(self._invoke_callbacks, names="selection")
        self.callbacks = callbacks

    @property
    def values(self):
        return self.items

    @values.setter
    def values(self, values):
        # if np.isdtype(np.asarray(values).dtype, "bool"):
        #     unique_values = np.asarray([True, False])
        # else:
        unique_values = np.unique(values)
        self.items = unique_values.tolist()

    @property
    def value(self):
        return tuple(self.selection)

    @value.setter
    def value(self, value):
        value = [_value for _value in value if _value in self.values]
        value = tuple(value)
        if value == self.value:
            return
        self.selection = list(value)

    @property
    def is_active(self):
        return len(self.value) > 0

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
