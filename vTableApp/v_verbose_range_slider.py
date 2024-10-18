import ipyvuetify as v

from .v_bounded_float_field import BoundedFloatField


class VerboseRangeSlider(v.Html):  # type: ignore
    def __init__(self, *, min, max, step, value=None, **kwargs):
        if value is None:
            value = (min, max)
        self._slider = v.RangeSlider(
            v_model=value,
            min=min,
            max=max,
            step=step,
            strict=True,
            thumb_label=True,
            class_="px-1",
        )
        self._lower = BoundedFloatField(
            value=min,
            min=min,
            max=max,
            step=step,
            label="Lower bound",
            class_="pa-2",
        )
        self._upper = BoundedFloatField(
            value=max,
            min=min,
            max=max,
            step=step,
            label="Upper bound",
            class_="pa-2",
        )
        self._slider.observe(self._set_fields, "v_model")
        self._lower.observe(self._set_lower, "value")
        self._upper.observe(self._set_upper, "value")
        super().__init__(
            tag="div",
            class_="d-flex flex-column",
            children=[
                self._slider,
                v.Html(  # type: ignore
                    tag="div",
                    class_="d-flex flex-row",
                    children=[self._lower, self._upper],
                ),
            ],
        )

    def _set_fields(self, change):
        if change["new"] == change["old"]:
            return
        value = min(change["new"]), max(change["new"])
        self._lower.max = value[1]
        self._upper.min = value[0]
        self._lower.value = value[0]
        self._upper.value = value[1]

    def _set_lower(self, change):
        if change["new"] == change["old"]:
            return
        try:
            value = float(change["new"])
        except ValueError:
            self._slider.v_model = (self._lower.min, self._slider.v_model[1])
            return
        if value == self._slider.v_model[0]:
            return
        self._slider.v_model = (value, self._slider.v_model[1])

    def _set_upper(self, change):
        if change["new"] == change["old"]:
            return
        try:
            value = float(change["new"])
        except ValueError:
            self._slider.v_model = (self._slider.v_model[0], self._slider.v_model[0])
            return
        if value == self._slider.v_model[1]:
            return
        self._slider.v_model = (self._slider.v_model[0], value)

    @property
    def step(self):
        return self._slider.step

    @step.setter
    def step(self, step):
        self._slider.step = step
        self._lower.step = step
        self._upper.step = step

    @property
    def min(self):
        return self._slider.min

    @min.setter
    def min(self, min):
        if min == self.min:
            return
        if min > self.max:
            raise ValueError("min > max")
        self._slider.min = min
        self._lower.min = min
        self._upper.min = min

    @property
    def max(self):
        return self._slider.max

    @max.setter
    def max(self, max):
        if max == self.max:
            return
        if max < self.min:
            raise ValueError("max < min")
        self._slider.max = max
        self._lower.max = max
        self._upper.max = max

    @property
    def value(self):
        return self._slider.v_model

    @value.setter
    def value(self, value):
        value = tuple(value)
        if value == self.value:
            return
        self._slider.v_model = value
