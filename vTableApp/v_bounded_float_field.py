import ipyvuetify as v
import traitlets


class BoundedFloatField(v.VuetifyTemplate):  # type: ignore
    label = traitlets.Unicode().tag(sync=True)
    value = traitlets.Float(default_value=0).tag(sync=True)
    min = traitlets.Float(default_value=0).tag(sync=True)
    max = traitlets.Float(default_value=1).tag(sync=True)
    step = traitlets.Float(default_value=0.1).tag(sync=True)
    error = traitlets.Any(default_value=None).tag(sync=True)
    readonly = traitlets.Bool(defaut_value=False, allow_none=False).tag(sync=True)
    class_ = traitlets.Unicode().tag(sync=True)
    style_ = traitlets.Unicode().tag(sync=True)

    @traitlets.default("template")
    def _template(self):
        return """
          <v-text-field
            type="number"
            v-model="Number(value)"
            :class="class_"
            :style="style_"
            :label="label"
            :readonly="readonly"
            :rules="[error]"
            :min="min" :max="max" :step="step"
            @input="validate"
          ></v-text-field>
        """

    @traitlets.observe("value")
    def _on_value_change(self, change):
        if change["new"] == change["old"]:
            return
        self.vue_validate(change["new"])

    def vue_validate(self, value):
        cast = float if self.step != 1 else int
        try:
            if isinstance(value, str) and len(value) == 0:
                raise ValueError("Input required")
            try:
                value = cast(value)
            except ValueError:
                raise ValueError(f"Input must be {cast}")
            if value < self.min or value > self.max:
                raise ValueError(
                    f"Input must fall within [{cast(self.min)}, {cast(self.max)}]"
                )
            if not round(value / self.step, 5).is_integer():
                raise ValueError(f"Input must be dividable by {cast(self.step)}")
            self.error = None
            self.value = value
        except ValueError as e:
            self.error = str(e)
