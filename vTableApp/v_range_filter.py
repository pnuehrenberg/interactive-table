from collections.abc import Iterable
from contextlib import contextmanager

import ipyvuetify as v
import numpy as np
import traitlets
from numpy.typing import NDArray

from .v_verbose_range_slider import VerboseRangeSlider


class RangeFilter(v.Col):
    allow_quantile_range_filter = traitlets.Bool().tag(sync=True)
    float_step = traitlets.Float(min=1e-6, allow_none=False).tag(sync=True)

    def __init__(
        self,
        values: Iterable,
        *,
        callbacks=None,
        allow_quantile_range_filter=True,
        float_step=1e-3,
    ):
        self.callbacks = None
        self.float_step = float_step
        self._value_range_slider = VerboseRangeSlider(
            min=0, max=1, step=1, round_to_step=False,
        )
        self._quantile_range_slider = VerboseRangeSlider(
            min=0, max=1, step=self.float_step, round_to_step=False,
        )
        super().__init__()
        self._window = None
        self._values = None
        self._window = v.Window(
            children=[
                v.WindowItem(children=[self._value_range_slider]),
                v.WindowItem(children=[self._quantile_range_slider]),
            ],
            v_model=0,
        )
        self.values = values
        # self._value_range_slider.value = (self.min, self.max)
        self._switch = v.Switch(v_model=0, label="Quantile range", class_="px-3")
        self.allow_quantile_range_filter = allow_quantile_range_filter
        self._enable_sliders()
        traitlets.link(
            (self._switch, "v_model"),
            (self._window, "v_model"),
            transform=(lambda v: int(v), lambda v: bool(v)),
        )
        self._value_range_slider._slider.observe(
            self._invoke_callbacks, names="v_model"
        )
        self._window.observe(self._invoke_callbacks, names="v_model")
        self._quantile_range_slider._slider.observe(
            self._invoke_callbacks, names="v_model"
        )
        self.callbacks = callbacks

    def _enable_sliders(self):
        if self.allow_quantile_range_filter:
            self.children = [self._switch, self._window]
        else:
            if self._switch.v_model:
                self._switch.v_model = False
            self.children = [self._window]

    @traitlets.observe("allow_quantile_range_filter")
    def _on_allow_quantile_range_filter_change(self, change):
        if change["new"] == change["old"]:
            return
        self._enable_sliders()

    @property
    def min(self):
        return self._value_range_slider.min

    @min.setter
    def min(self, min):
        self._value_range_slider.min = float(min)

    @property
    def max(self):
        return self._value_range_slider.max

    @max.setter
    def max(self, max):
        self._value_range_slider.max = float(max)

    @property
    def step(self):
        return self._value_range_slider.step

    @step.setter
    def step(self, step):
        self._value_range_slider.step = step

    @property
    def values(self) -> NDArray:
        if self._values is None:
            raise ValueError("values not initialized")
        return self._values

    @values.setter
    def values(self, values):
        values = np.asarray(values)
        self._values = values
        self.step = (
            1 if np.issubdtype(np.asarray(values).dtype, int) else self.float_step
        )
        _min = np.min(self.values)
        _max = np.max(self.values)
        if _min > self.max:
            self.max = _max
            self.min = _min
        else:
            self.min = _min
            self.max = _max
        value = self._value_range_slider.value
        with self.block_callbacks():
            self._value_range_slider.value = (
                max(self.min, value[0]),
                min(self.max, value[1]),
            )

    @property
    def value(self):
        if self._window is None:
            raise ValueError("not initialized")
        if self._window.v_model == 0:
            return tuple(self._value_range_slider.value)
        return tuple(self._quantile_range_slider.value)

    @value.setter
    def value(self, value):
        value = tuple(value)
        if value == self.value:
            return
        if self._window is None:
            return
        if self._window.v_model == 0:
            self._value_range_slider.value = value
            return
        self._quantile_range_slider.value = value

    def reset(self):
        self._value_range_slider.value = (self.min, self.max)
        self._quantile_range_slider.value = (0, 1)

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
        if self._window is None:
            return
        range_type = "value_range" if self._window.v_model == 0 else "quantile_range"
        for callback in self.callbacks:
            callback((range_type, self.value))
