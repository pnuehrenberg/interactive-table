import ipyvuetify as v
import traitlets


class BoundedInput(v.VuetifyTemplate):  # type: ignore
    template_file = (__file__, "templates/BoundedInput.vue")

    min = traitlets.Any().tag(sync=True)
    max = traitlets.Any().tag(sync=True)
    step = traitlets.Any().tag(sync=True)
    value = traitlets.Float().tag(sync=True)
    temp_value = traitlets.Any().tag(sync=True)
    label = traitlets.Any().tag(sync=True)
    readonly = traitlets.Bool(defaut_value=False, allow_none=False).tag(sync=True)
    class_ = traitlets.Unicode().tag(sync=True)
    style_ = traitlets.Unicode().tag(sync=True)

    def __init__(
        self,
        *,
        min,
        max,
        step,
        value=None,
        label=None,
        readonly=False,
        class_="",
        style_="",
    ):
        self.min = min
        self.max = max
        self.step = step
        self.value = value if value is not None else min
        self.temp_value = self.value
        self.label = label
        self.readonly = readonly
        self.class_ = class_
        self.style_ = style_
        super().__init__()

    @traitlets.observe("temp_value")
    def _on_temp_value_change(self, change):
        if change["new"] == change["old"]:
            return
        try:
            value = float(change["new"])
        except ValueError:
            return
        if value == self.value or value < self.min or value > self.max:
            return
        if self.step == 1 and (
            (value != self.min or value != self.max) and value % 1 != 0
        ):
            return
        self.value = value

    @traitlets.observe("value")
    def _on_value_change(self, change):
        if change["new"] == change["old"]:
            return
        value = change["new"]
        if self.temp_value is None:
            return
        if value == self.temp_value:
            return
        self.temp_value = value
