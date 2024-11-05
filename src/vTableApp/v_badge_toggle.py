import ipywidgets as widgets
import ipyvuetify as v
import traitlets

class BadgeToggle(v.VuetifyTemplate):
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
                    icon="mdi-close"
                    style="cursor: pointer"
                    :color="hover ? 'red' : 'red lighten-2'"
                    overlap
                    @click.native="on_badge_click"
                    >
                    <jupyter-widget :widget="content" @click.native.stop="on_content_click"/>
                </v-badge>
            </v-hover>
        </v-template>
        """

    def __init__(
        self,
        *,
        content,
        on_badge_click_callbacks=None,
        on_content_click_callbacks=None,
    ):
        self.active = False
        self.content = content
        self.on_badge_click_callbacks = on_badge_click_callbacks
        self.on_content_click_callbacks = on_content_click_callbacks
        super().__init__()

    def _invoke_callbacks(self, callbacks):
        if callbacks is None:
            return True
        for callback in callbacks:
            if not callback():
                return False
        return True

    def set_active(self, active):
        self.active = active
        return True

    def vue_on_badge_click(self, data):
        self._invoke_callbacks(self.on_badge_click_callbacks)

    def vue_on_content_click(self, data):
        self._invoke_callbacks(self.on_content_click_callbacks)
