from typing import Any

import ipyvuetify as v
import traitlets


def step_floor(value, step):
    if step == 0:
        return value
    remainder = value % step
    if remainder == 0:
        return value
    return value - remainder


def step_ceil(value, step):
    if step == 0:
        return value
    remainder = value % step
    if remainder == 0:
        return value
    return value - remainder + step


class BoundedNumberField(v.VuetifyTemplate):  # type: ignore
    label = traitlets.Unicode().tag(sync=True)
    number_text = traitlets.Unicode(allow_none=True).tag(sync=True)
    min = traitlets.Float().tag(sync=True)
    max = traitlets.Float().tag(sync=True)
    min_rounded = traitlets.Float().tag(sync=True)
    max_rounded = traitlets.Float().tag(sync=True)
    step = traitlets.Float().tag(sync=True)
    round_to_step = traitlets.Bool(default_value=False).tag(sync=True)
    error = traitlets.Any(default_value=None).tag(sync=True)
    readonly = traitlets.Bool(defaut_value=False, allow_none=False).tag(sync=True)
    class_ = traitlets.Unicode().tag(sync=True)
    style_ = traitlets.Unicode().tag(sync=True)

    @traitlets.default("template")
    def _template(self):
        return """
          <v-text-field
            type="number"
            v-model="number_text"
            :class="class_"
            :style="style_"
            :label="label"
            :readonly="readonly"
            :rules="[error]"
            :min="min_rounded" :max="max_rounded" :step="step"
            @input="validate"
            @change="coerce"
          ></v-text-field>
        """

    def __init__(self, *args, value=None, **kwargs):
        super().__init__(*args, **kwargs)
        if value is None:
            value = self.min
        self.value = value

    @property
    def value(self):
        if self.error is not None:
            raise ValueError(self.error)
        return float(self.number_text)  # type: ignore

    @value.setter
    def value(self, value):
        if self.step == 1:
            value = int(value)
        self.number_text = str(value)
        if self.error is not None:
            raise ValueError(self.error)

    @traitlets.observe("min")
    def _on_min_change(self, change):
        self.min_rounded = step_floor(self.min, self.step)

    @traitlets.observe("max")
    def _on_max_change(self, change):
        self.max_rounded = step_ceil(self.max, self.step)

    @traitlets.observe("step")
    def _on_step_change(self, change):
        self.min_rounded = step_floor(self.min, self.step)
        self.max_rounded = step_ceil(self.max, self.step)

    @traitlets.observe("number_text")
    def _on_text_change(self, change):
        self.vue_validate(self.number_text)

    def vue_validate(self, value):
        dtype: Any = float if self.step != 1 else int
        cast = dtype
        if cast is int:
            def cast(v):
                return int(float(v))
        try:
            if len(value) == 0:
                raise ValueError("Input required")
            cast(value)
            try:
                number_value = cast(value)
            except ValueError:
                raise ValueError(f"Input is not {cast}")
            if number_value < self.min or number_value > self.max:
                raise ValueError(f"Input {number_value} out of range [{cast(self.min)}, {cast(self.max)}]")
            self.number_text = value
            self.error = None
        except Exception as e:
            self.number_text = value
            self.error = str(e)

    def vue_coerce(self, value):
        if len(value) == 0:
            return
        number_value = float(value)
        if number_value < self.min:
            number_value = self.min
        elif number_value > self.max:
            number_value = self.max
        elif self.round_to_step:
            number_floor = step_floor(number_value, self.step)
            number_ceil = step_ceil(number_value, self.step)
            if number_value - number_floor > number_ceil - number_value:
                number_value = number_ceil
            else:
                number_value = number_floor
            number_value = round(number_value, 6)
        if self.step == 1:
            number_value = int(number_value)
        self.number_text = str(number_value)
        self.error = None
