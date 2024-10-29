from typing import Any

import ipyvuetify as v
import traitlets


class _ResetButton(v.VuetifyTemplate):  # type: ignore
    class_ = traitlets.Unicode().tag(sync=True)
    style_ = traitlets.Unicode().tag(sync=True)
    reset_icon = traitlets.Unicode().tag(sync=True)

    @traitlets.default("template")
    def _template(self):
        return """
<template>
  <v-btn
    @click.stop="button_click"
    icon
    :class="class_"
    :style="style_"
  >
   <v-icon small>{{ reset_icon }}</v-icon>
  </v-btn>
</template>
"""

    def __init__(self, *args, callbacks=None, **kwargs):
        self.callbacks = [] if callbacks is None else callbacks
        assert isinstance(self.callbacks, list)
        super().__init__(*args, **kwargs)

    def _invoke_callbacks(self):
        for callback in self.callbacks:
            callback()

    def vue_button_click(self, *args):
        self._invoke_callbacks()

    def show(self):
        self.class_ = self.class_.replace("d-none", "")

    def hide(self):
        if "d-none" in self.class_:
            return
        self.class_ = f"{self.class_} d-none"


class CheckableExpansionPanel(v.ExpansionPanel):
    checked = traitlets.Bool(allow_none=False).tag(sync=True)

    def __init__(
        self,
        title,
        content,
        *,
        checked=False,
        show_reset_button=True,
        only_show_reset_button_when_checked=True,
        reset_icon="mdi-close",
        reset_callbacks=None,
    ):
        self.show_reset_button = show_reset_button
        self.only_show_reset_button_when_checked = only_show_reset_button_when_checked
        self.reset_button = _ResetButton(
            reset_icon=reset_icon,
            callbacks=reset_callbacks,
            style_="max-width: 30px; max-height: 30px",
        )
        header_content: list[Any] = [title]
        if self.show_reset_button:
            header_content.extend([v.Spacer(), self.reset_button])
        if (
            self.show_reset_button
            and self.only_show_reset_button_when_checked
            and not checked
        ):
            self.reset_button.hide()
        self.header = v.ExpansionPanelHeader(children=header_content)
        self.checked = checked
        self.reset_callbacks = reset_callbacks
        super().__init__(
            children=[
                self.header,
                v.ExpansionPanelContent(children=content),
            ]
        )

    def _invoke_reset_callbacks(self, *args):
        if self.reset_callbacks is None:
            return
        for callback in self.reset_callbacks:
            callback()

    @traitlets.observe("checked")
    def _on_checked_change(self, change):
        if change["new"] == change["old"]:
            return
        if self.checked:
            self.header.expand_icon = "mdi-check-circle"
        else:
            self.header.expand_icon = "$expand"
        self.header.disable_icon_rotate = self.checked
        if (
            self.show_reset_button
            and self.only_show_reset_button_when_checked
            and not self.checked
        ):
            self.reset_button.hide()
        elif self.show_reset_button and self.only_show_reset_button_when_checked:
            self.reset_button.show()
