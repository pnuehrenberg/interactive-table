import ipyvuetify as v

from .v_bounded_number_field import BoundedNumberField, step_ceil, step_floor


class VerboseRangeSlider(v.Html):  # type: ignore
    def __init__(self, *, min, max, step, round_to_step=True, value=None, **kwargs):
        if value is None:
            value = (min, max)
        self._slider = v.RangeSlider(
            v_model=value,
            min=step_floor(min, step),
            max=step_ceil(max, step),
            step=0,
            strict=True,
            class_="px-1",
        )
        self._lower = BoundedNumberField(
            value=min,
            min=min,
            max=max,
            step=step,
            round_to_step=round_to_step,
            label="Lower bound",
            class_="pa-2",
            style_="width: 50%",
        )
        self._upper = BoundedNumberField(
            value=max,
            min=min,
            max=max,
            step=step,
            round_to_step=round_to_step,
            label="Upper bound",
            class_="pa-2",
            style_="width: 50%",
        )
        self._slider.observe(self._set_fields, "v_model")
        self._lower.observe(self._set_lower, "number_text")
        self._upper.observe(self._set_upper, "number_text")
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
        value = float(min(change["new"])), float(max(change["new"]))
        self._lower.value = min(max(value[0], self._lower.min), self._upper.max)
        self._upper.value = max(min(value[1], self._upper.max), self._lower.min)

    def _set_lower(self, change):
        if change["new"] == change["old"]:
            return
        try:
            value = self._lower.value
        except ValueError:
            return
        if value == self._slider.v_model[0]:
            return
        self._slider.v_model = (value, self._slider.v_model[1])

    def _set_upper(self, change):
        if change["new"] == change["old"]:
            return
        try:
            value = self._upper.value
        except ValueError:
            return
        if value == self._slider.v_model[1]:
            return
        self._slider.v_model = (self._slider.v_model[0], value)

    @property
    def step(self):
        return self._lower.step

    @step.setter
    def step(self, step):
        if step == 1:
            self._slider.step = step
        else:
            self._slider.step = 0
        self._lower.step = step
        self._upper.step = step
        # and recalculate min and max for slider
        self.min = self.min
        self.max = self.max

    @property
    def min(self):
        return self._lower.min

    @min.setter
    def min(self, min):
        if min > self.max:
            raise ValueError(f"min {min} > max {self.max}")
        self._slider.min = step_floor(min, self.step)
        self._lower.min = min
        self._upper.min = min

    @property
    def max(self):
        return self._upper.max

    @max.setter
    def max(self, max):
        if max < self.min:
            raise ValueError(f"max {max} < min {self.min}")
        self._slider.max = step_ceil(max, self.step)
        self._lower.max = max
        self._upper.max = max

    @property
    def value(self):
        return self._lower.value, self._upper.value

    @value.setter
    def value(self, value):
        value = tuple(value)
        if value == self.value:
            return
        self._slider.v_model = value
        # self._lower.value, self._upper.value = value
