import ipyvuetify as v


class CallbacksButton(v.Btn):
    def __init__(self, *args, callbacks=None, **kwargs):
        self.callbacks = [] if callbacks is None else callbacks
        assert isinstance(self.callbacks, list)
        super().__init__(*args, **kwargs)
        self.on_event("click", lambda *args: self._invoke_callbacks())

    def _invoke_callbacks(self):
        for callback in self.callbacks:
            callback()
