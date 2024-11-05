import ipyvuetify as v
import ipywidgets as widgets
import traitlets


class Menu(v.VuetifyTemplate):  # type: ignore
    title = traitlets.Unicode().tag(sync=True)
    menu = traitlets.Bool().tag(sync=True)
    fullscreen = traitlets.Bool().tag(sync=True)

    open_button = traitlets.Unicode().tag(sync=True)
    open_button_icon = traitlets.Bool().tag(sync=True)
    open_button_class = traitlets.Unicode().tag(sync=True)

    confirm_button = traitlets.Unicode().tag(sync=True)
    confirm_button_icon = traitlets.Bool().tag(sync=True)

    close_button = traitlets.Unicode().tag(sync=True)
    close_button_icon = traitlets.Bool().tag(sync=True)

    content = traitlets.List().tag(sync=True, **widgets.widget_serialization)
    actions = traitlets.List().tag(sync=True, **widgets.widget_serialization)

    def __init__(
        self,
        open_button,
        title="",
        open_button_icon=False,
        open_button_class="ma-2",
        confirm_button="mdi-check",
        confirm_button_icon=True,
        close_button="mdi-close",
        close_button_icon=True,
        content=None,
        actions=None,
        open_menu_on_init=False,
        on_open_callbacks=None,
        on_submit_callbacks=None,
        on_close_callbacks=None,
    ):
        self.title = title
        self.open_button = open_button
        self.open_button_icon = open_button_icon
        self.confirm_button = confirm_button
        self.confirm_button_icon = confirm_button_icon
        self.close_button = close_button
        self.close_button_icon = close_button_icon
        self.content = [] if content is None else content
        self.actions = [] if actions is None else actions
        self.menu = open_menu_on_init
        self.on_open_callbacks = [] if on_open_callbacks is None else on_open_callbacks
        self.on_submit_callbacks = (
            [] if on_submit_callbacks is None else on_submit_callbacks
        )
        self.on_close_callbacks = (
            [] if on_close_callbacks is None else on_close_callbacks
        )
        super().__init__()

    def _invoke_callbacks(self, callbacks):
        if callbacks is None:
            return True
        for callback in callbacks:
            if not callback():
                return False
        return True

    @traitlets.observe("menu")
    def _on_menu_change(self, change):
        if change["old"] == change["new"]:
            return
        if not self.menu:
            self._invoke_callbacks(self.on_close_callbacks)
        else:
            self._invoke_callbacks(self.on_open_callbacks)

    def vue_confirm(self, *args):
        self._invoke_callbacks(self.on_submit_callbacks)
        self.menu = False

    @traitlets.default("template")
    def _template(self):
        return """
            <template>
                <v-menu
                    v-model="menu"
                    :close-on-content-click="false"
                    >
                    <template v-slot:activator="{ on, attrs }">
                        <v-btn
                            :icon="open_button_icon"
                            v-bind="attrs"
                            v-on="on"
                            :class="open_button_class"
                            >
                            <v-icon v-if="open_button_icon">{{ open_button }}</v-icon>
                            <div v-else>
                                {{ open_button }}
                            </div>
                        </v-btn>
                    </template>
                    <v-btn class="d-none"></v-btn>
                    <!--Hacky, add hidden focusable element to prevent focus on others.-->
                    <v-card>
                        <v-card-title v-if="title || close_button" class=pa-4>
                            <span class="text-h5">{{ title }}</span>
                            <v-spacer></v-spacer>
                            <v-btn
                                v-if="close_button"
                                :icon="close_button_icon"
                                @click="menu = false"
                                >
                                <v-icon v-if="close_button_icon">{{ close_button }}</v-icon>
                                <div v-else>
                                    {{ close_button }}
                                </div>
                            </v-btn>
                        </v-card-title>
                        <v-divider v-if="content.length > 0"></v-divider>
                        <jupyter-widget v-for="item in content" :widget="item" />
                        <v-divider v-if="confirm_button || actions.length > 0"></v-divider>
                        <v-card-actions v-if="confirm_button || actions.length > 0" class="d-flex flex-row pa-4">
                            <jupyter-widget v-for="item in actions" :widget="item" class="pa-2 align-self-center"/>
                            <v-btn
                                v-if="confirm_button"
                                :icon="confirm_button_icon"
                                @click="confirm"
                                class="pa-2"
                                >
                                <v-icon v-if="confirm_button_icon">{{ confirm_button }}</v-icon>
                                <div v-else>
                                    {{ confirm_button }}
                                </div>
                            </v-btn>
                        </v-card-actions>
                    </v-card>
                </v-menu>
            </template>
            """
