from collections.abc import Iterable
from contextlib import contextmanager

import ipyvuetify as v
import numpy as np
import traitlets
from numpy.typing import NDArray

from .v_bounded_slider import BoundedSlider


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
        class_="ma-0 pa-0",
    ):
        self.callbacks = None
        self.float_step = float_step
        self._value_range_slider = BoundedSlider(
            min=0,
            max=1,
            step=1,
            class_="d-flex flex-column",
            style_="width: 100%",
        )
        self._quantile_range_slider = BoundedSlider(
            min=0,
            max=1,
            step=self.float_step,
            class_="d-flex flex-column",
            style_="width: 100%",
        )
        super().__init__(class_=class_)
        self._values = None
        self.values = values
        # self._value_range_slider.value = (self.min, self.max)
        self._switch = v.Switch(
            v_model=0,
            label="Quantile range",
            hide_details=True,
            class_="pa-0 ma-0 mb-2",
        )
        self.allow_quantile_range_filter = allow_quantile_range_filter
        self._enable_sliders()
        self._switch.observe(self._set_sliders, names="v_model")
        self._value_range_slider.observe(self._invoke_callbacks, names="temp_range")
        self._quantile_range_slider.observe(self._invoke_callbacks, names="temp_range")
        self.callbacks = callbacks

    def _set_sliders(self, change):
        active_slider = (
            self._value_range_slider if not self._switch.v_model
            else self._quantile_range_slider
        )
        self.children = [self._switch, active_slider]
        self._invoke_callbacks()

    def _enable_sliders(self):
        if self.allow_quantile_range_filter:
            active_slider = (
                self._value_range_slider if not self._switch.v_model
                else self._quantile_range_slider
            )
            self.children = [self._switch, active_slider]
        else:
            if self._switch.v_model:
                self._switch.v_model = False
            self.children = [self._value_range_slider]

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
        if not self.allow_quantile_range_filter or not self._switch.v_model:
            return tuple(self._value_range_slider.value)
        return tuple(self._quantile_range_slider.value)

    @value.setter
    def value(self, value):
        value = tuple(value)
        if value == self.value:
            return
        if not self.allow_quantile_range_filter or not self._switch.v_model:
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
        range_type = (
            "value_range"
            if not self.allow_quantile_range_filter or not self._switch.v_model
            else "quantile_range"
        )
        for callback in self.callbacks:
            callback((range_type, self.value))
