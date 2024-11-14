import ipyvuetify as v
import ipywidgets as widgets
import traitlets

from .v_bounded_input import BoundedInput


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


class BoundedSlider(v.VuetifyTemplate):  # type: ignore
    template_file = (__file__, "templates/RangeSliderInput.vue")

    min = traitlets.Any().tag(sync=True)
    max = traitlets.Any().tag(sync=True)
    step = traitlets.Any().tag(sync=True)
    temp_range = traitlets.Tuple(traitlets.Any(), traitlets.Any()).tag(sync=True)
    lower = traitlets.Any().tag(sync=True, **widgets.widget_serialization)
    upper = traitlets.Any().tag(sync=True, **widgets.widget_serialization)
    class_ = traitlets.Unicode().tag(sync=True)
    style_ = traitlets.Unicode().tag(sync=True)

    def __init__(
        self,
        *,
        min,
        max,
        step,
        value=None,
        label_lower="Lower bound",
        label_upper="Upper bound",
        class_="d-inline-flex flex-column ma-2",
        style_="",
    ):
        self.class_ = class_
        self.style_ = style_
        self.min = min
        self.max = max
        self.step = step
        self.lower = BoundedInput(
            min=min,
            max=max,
            step=step,
            value=min,
            label=label_lower,
            class_="mx-2",
            style_="width: 100%",
        )
        self.upper = BoundedInput(
            min=min,
            max=max,
            step=step,
            value=max,
            label=label_upper,
            class_="mx-2",
            style_="width: 100%",
        )
        self._link()
        if value is None:
            value = (min, max)
        else:
            value = sorted(value)
        self.temp_range = self._round_to_step(value[0]), self._round_to_step(value[1])
        super().__init__()

    def _clip_to_range(self, value):
        if value < self.min:
            return self.min
        if value > self.max:
            return self.max
        return value

    def _get_lower(self, range):
        return self._clip_to_range(min(map(float, range)))

    def _get_upper(self, range):
        return self._clip_to_range(max(map(float, range)))

    def _round_to_step(self, value):
        if value == self.min:
            return step_floor(value, self.step)
        elif value == self.max:
            return step_ceil(value, self.step)
        floor = step_floor(value, self.step)
        ceil = step_ceil(value, self.step)
        if ceil - value < value - floor:
            return ceil
        return floor

    def _link(self):
        traitlets.link(
            (self.lower, "value"),
            (self, "temp_range"),
            transform=(
                lambda value: (self._round_to_step(value), self.upper.value),
                lambda range: self._get_lower(range),
            ),
        )
        traitlets.link(
            (self.upper, "value"),
            (self, "temp_range"),
            transform=(
                lambda value: (self.lower.value, self._round_to_step(value)),
                lambda range: self._get_upper(range),
            ),
        )
        traitlets.link((self.upper, "step"), (self, "step"))
        traitlets.link((self.lower, "step"), (self, "step"))
        traitlets.link((self.upper, "min"), (self, "min"))
        traitlets.link((self.lower, "min"), (self, "min"))
        traitlets.link((self.upper, "max"), (self, "max"))
        traitlets.link((self.lower, "max"), (self, "max"))

    @property
    def value(self):
        return (self.lower.value, self.upper.value)

    @value.setter
    def value(self, value):
        value = tuple(sorted(value))
        if value == self.value:
            return
        self.temp_range = self._round_to_step(value[0]), self._round_to_step(value[1])
