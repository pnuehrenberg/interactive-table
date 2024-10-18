import ipyvuetify as v
import traitlets


class CheckableExpansionPanel(v.ExpansionPanel):
    checked = traitlets.Bool(allow_none=False).tag(sync=True)

    def __init__(self, title, content, *, checked=False):
        self.header = v.ExpansionPanelHeader(children=[title])
        self.checked = checked
        super().__init__(
            children=[
                self.header,
                v.ExpansionPanelContent(children=content),
            ]
        )

    @traitlets.observe("checked")
    def _on_checked_change(self, change):
        if change["new"] == change["old"]:
            return
        if self.checked:
            self.header.expand_icon = "mdi-check-circle"
        else:
            self.header.expand_icon = "$expand"
        self.header.disable_icon_rotate = self.checked
