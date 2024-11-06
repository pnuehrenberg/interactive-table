import ipyvuetify as v
import ipywidgets as widgets
import traitlets


class BadgeToggle(v.VuetifyTemplate):  # type: ignore
    active = traitlets.Bool().tag(sync=True)
    content = traitlets.Any().tag(sync=True, **widgets.widget_serialization)

    @traitlets.default("template")
    def _template(self):
        return """
        <v-template>
            <v-hover v-slot="{ hover }">
                <v-badge
                    class="ma-2"
                    :value="active"
                    :icon="hover ? 'mdi-close' : 'mdi-check'"
                    style="cursor: pointer"
                    :color="hover ? 'primary' : 'primary lighten-2'"
                    inline
                    @click.native.stop="active = false"
                    >
                    <jupyter-widget :widget="content" @click.native.stop/>
                </v-badge>
            </v-hover>
        </v-template>
        """

    def __init__(
        self,
        *,
        content,
        on_activate_callbacks=None,
        on_deactivate_callbacks=None,
    ):
        self.active = False
        self.content = content
        self.on_activate_callbacks = on_activate_callbacks
        self.on_deactivate_callbacks = on_deactivate_callbacks
        super().__init__()

    def _invoke_callbacks(self, callbacks):
        if callbacks is None:
            return True
        for callback in callbacks:
            if not callback():
                return False
        return True

    @traitlets.observe("active")
    def _on_active_change(self, change):
        if change["old"] == change["new"]:
            return
        if self.active:
            self._invoke_callbacks(self.on_activate_callbacks)
        else:
            self._invoke_callbacks(self.on_deactivate_callbacks)
