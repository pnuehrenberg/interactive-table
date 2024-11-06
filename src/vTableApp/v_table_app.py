import ipyvuetify as v

from .v_callbacks_button import CallbacksButton
from .v_content_with_sidebar import ContentWithSidebar
from .v_dataframe_filter import lazy_filter
from .v_dialog import Dialog
from .v_table_display import TableDisplay


class TableApp(ContentWithSidebar):
    def __init__(self, dataframe, filter_dependencies=None, enable_validation=True):
        self.table_display = TableDisplay(
            dataframe  # , on_edit_callbacks=[self._update_filters_on_edit]
        )
        self.lazyfilter = lazy_filter(
            self.table_display,
            dependencies=filter_dependencies,
            track_description=True,
            callbacks=[lambda df: self.table_display._set_items(index=df.index)],
        )
        self.filters = v.Col(
            children=[
                v.CardTitle(children=["Filters"]),
                self.lazyfilter,
            ],
            class_="pa-2",
        )
        self.filters.hide()

        self.filter_button = CallbacksButton(
            class_="ma-2",
            icon=True,
            children=[v.Icon(children=["mdi-filter"])],
        )

        # self.edit = EditDialog(
        #     self.table_display,
        #     submit_callbacks=[
        #         self._update_filters_on_edit,
        #     ],
        # )
        # self.validation_button = None
        # if enable_validation and "valid" in self.table_display.dataframe.columns:
        #     self.validation_button = CallbacksButton(
        #         class_="ma-2",
        #         icon=True,
        #         children=[v.Icon(children=["mdi-check"])],
        #         callbacks=[self._set_row_valid],
        #     )
        self.fullscreen = Dialog(
            open_button="mdi-fullscreen",
            open_button_icon=True,
            confirm_button="",
            fullscreen=True,
            content=[self._fullscreen_content],
        )
        # self.buttons = v.Html(  # type: ignore
        #     tag="div",
        #     class_="d-inline flex grey lighten-2 ma-2 flex-column align-self-start",
        #     style_="border-radius: 10px",
        #     children=self._get_buttons(),
        # )
        # self.table_display.observe(self._set_edit_data, "selected")

        super().__init__(
            sidebar_content=[
                self.filter_button,
                self.fullscreen,
                self.filters,
            ],  # self.buttons,
            content=[self.table_display],
            toggle_sidebar_button=self.filter_button,
            # toggle_callbacks=[
            #     lambda: self.buttons.class_list.toggle("flex-column", "flex-row")
            # ],
            shrink_callbacks=[lambda: self.filters.hide()],
            expand_callbacks=[lambda: self.filters.show()],
        )

    def _update_filters_on_edit(self):
        selection = {
            value[0]: (value[1], value[3])
            for value in self.lazyfilter.description.values()
        }
        self.lazyfilter.update(selection, validate_selection=True, reset_on_error=True)
        self.lazyfilter.apply()

    # def _set_edit_data(self, change):
    #     rows = self.table_display.selected
    #     if len(rows) == 0:
    #         row_data = None
    #     else:
    #         row_data = self.table_display.dataframe.loc[int(rows[0]["index"])]
    #     self.edit.row_data = row_data

    # def _set_row_valid(self):
    #     if self.edit.row_data is None:
    #         return
    #     self.table_display.dataframe.at[self.edit.row_data.name, "valid"] = True
    #     self.table_display._set_items(index=self.table_display.current_index)
    #     self._update_filters_on_edit()

    # def _get_buttons(self, *, include_fullscreen=True):
    #     buttons: List[Any] = [self.filter_button]  # , self.edit
    #     # if self.validation_button is not None:
    #     #     buttons.append(self.validation_button)
    #     if include_fullscreen:
    #         buttons.append(self.fullscreen)
    #     return buttons

    @property
    def _fullscreen_content(self):
        # buttons = v.Html(  # type: ignore
        #     tag="div",
        #     class_="d-inline flex grey lighten-2 ma-2 flex-column align-self-start",
        #     style_="border-radius: 10px",
        #     children=self._get_buttons(include_fullscreen=False),
        # )
        return ContentWithSidebar(
            sidebar_content=[self.filter_button, self.filters],  # buttons,
            content=[self.table_display],
            toggle_sidebar_button=self.filter_button,
            # toggle_callbacks=[
            #     lambda: buttons.class_list.toggle("flex-column", "flex-row")
            # ],
            shrink_callbacks=[lambda: self.filters.hide()],
            expand_callbacks=[lambda: self.filters.show()],
        )
