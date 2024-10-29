import ipyvuetify as v


class Dialog(v.Html):  # type: ignore
    def __init__(
        self,
        *,
        open_dialog_button,
        fullscreen=True,
        title="",
        width="650px",
        content=None,
        open_callbacks=None,
        post_open_callbacks=None,
        close_callbacks=None,
    ):
        self.open_dialog_button = open_dialog_button
        self.close_dialog_button = v.Btn(
            icon=True,
            children=[v.Icon(children=["mdi-window-close"])],
        )
        self.dialog_content = v.Card(
            children=[
                v.CardTitle(children=[title, v.Spacer(), self.close_dialog_button])
            ],
            class_="pa-0",
        )
        if content is not None:
            self.dialog_content.children = [*self.dialog_content.children, *content]
        self.dialog = v.Dialog(
            v_model="dialog",
            fullscreen=fullscreen,
            children=[self.dialog_content],
        )
        if not fullscreen:
            self.dialog.max_width = width
        self.open_dialog_button.on_event("click", self._open_dialog)
        self.close_dialog_button.on_event("click", self._close_dialog)
        self.dialog.v_model = False
        self.open_callbacks = open_callbacks
        self.post_open_callbacks = post_open_callbacks
        self.close_callbacks = close_callbacks
        super().__init__(
            tag="div", class_="d-flex", children=[self.open_dialog_button, self.dialog]
        )

    def _invoke_callbacks(self, callbacks):
        if callbacks is None:
            return True
        for callback in callbacks:
            if not callback():
                return False
        return True

    def _open_dialog(self, *args):
        self._invoke_callbacks(self.open_callbacks)
        self.dialog.v_model = True
        self._invoke_callbacks(self.post_open_callbacks)

    def _close_dialog(self, *args):
        self.dialog.v_model = False
        self._invoke_callbacks(self.close_callbacks)
