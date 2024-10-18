import ipyvuetify as v
import traitlets

# col_1 = v.Container(children=[item_1, item_1], class_="fluid d-flex flex-column flex-grow-1 fill-parent-height pa-0", style_="max-width: 200px; overflow-y: auto")
# col_2 = v.Container(children=[item_2], class_="fluid d-flex flex-column flex-grow-1 fill-parent-height pa-0", style_="overflow-y: auto")
# row = v.Container(children=[col_1, col_2], class_="fluid d-flex flex-row flex-grow-1 pa-0", style_="min-height: 300px")


class ContentWithSidebar(v.Container):
    expanded = traitlets.Bool(default_value=False, allow_none=False).tag(sync=True)

    def __init__(
        self,
        *,
        sidebar_content,
        content,
        toggle_sidebar_button,
        toggle_callbacks=None,
        shrink_callbacks=None,
        expand_callbacks=None,
        mini_sidebar_width="70px",
        expanded_sidebar_width="400px",
    ):
        self.mini_sidebar_width = mini_sidebar_width
        self.expanded_sidebar_width = expanded_sidebar_width
        self.sidebar = v.Container(
            class_="fluid d-flex flex-column flex-grow-1 fill-parent-height pa-0",
            children=sidebar_content,
            style_=f"max-width: {self.mini_sidebar_width}; overflow-y: auto",
        )
        self.content = v.Container(
            class_="fluid d-flex flex-column flex-grow-1 fill-parent-height pa-0",
            children=content,
            style_="overflow-y: auto",
        )
        toggle_sidebar_button.callbacks.append(self._toggle_sidebar)
        self.toggle_callbacks = toggle_callbacks
        self.shrink_callbacks = shrink_callbacks
        self.expand_callbacks = expand_callbacks
        super().__init__(
            class_="fluid d-flex flex-row flex-grow-1 pa-0",
            children=[self.sidebar, self.content],
            style_="max-height: 92.5dvh",
        )
        self.expanded = False

    def _toggle_sidebar(self, *args):
        self.expanded = not self.expanded

    @traitlets.observe("expanded")
    def _on_expanded_change(self, change):
        if change["new"] == change["old"]:
            return
        if self.sidebar.style_ is None:
            width = self.expanded_sidebar_width if not self.expanded else self.mini_sidebar_width
            self.sidebar.style_ = f"max-width: {width}"
        if self.toggle_callbacks is not None:
            for callback in self.toggle_callbacks:
                callback()
        if self.expanded:
            self.sidebar.style_ = self.sidebar.style_.replace(
                f"max-width: {self.mini_sidebar_width}",
                f"max-width: {self.expanded_sidebar_width}",
            )
            if self.expand_callbacks is not None:
                for callback in self.expand_callbacks:
                    callback()
        else:
            if self.shrink_callbacks is not None:
                for callback in self.shrink_callbacks:
                    callback()
            self.sidebar.style_ = self.sidebar.style_.replace(
                f"max-width: {self.expanded_sidebar_width}",
                f"max-width: {self.mini_sidebar_width}",
            )
