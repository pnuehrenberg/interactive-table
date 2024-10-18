import ipyvuetify as v

from .v_callbacks_button import CallbacksButton
from .v_content_with_sidebar import ContentWithSidebar
from .v_dataframe_filter import lazy_filter
from .v_dialog import Dialog
from .v_row_edit_dialog import EditDialog
from .v_table_display import TableDisplay


class TableApp(ContentWithSidebar):
    def __init__(self, dataframe, filter_dependencies=None):
        self.table_display = TableDisplay(dataframe)
        self.lazyfilter = lazy_filter(
            self.table_display,
            dependencies=filter_dependencies,
            track_description=True,
            callbacks=[lambda df: self.table_display._set_items(index=df.index)],
            class_="pa-4",
        )
        self.filters = v.Col(
            children=[
                v.CardTitle(children=["Filters"]),
                self.lazyfilter,
            ],
            class_="pa-4",
        )
        self.filter_button = CallbacksButton(
            class_="flex-grow-0 ma-2",
            icon=True,
            children=[v.Icon(children=["mdi-filter"])],
        )
        self.edit_button = v.Btn(
            class_="flex-grow-0 ma-2",
            icon=True,
            children=[v.Icon(children=["mdi-table-edit"])],
        )
        self.fullscreen_button = v.Btn(
            class_="flex-grow-0 ma-2",
            icon=True,
            children=[v.Icon(children=["mdi-fullscreen"])],
        )

        self.buttons = v.Html(  # type: ignore
            tag="div", class_="d-flex flex-column justify-start", children=[]
        )

        self.filters.hide()
        super().__init__(
            sidebar_content=[self.buttons, self.filters],
            content=[self.table_display],
            toggle_sidebar_button=self.filter_button,
            toggle_callbacks=[
                lambda: self.buttons.class_list.toggle("flex-column", "flex-row")
            ],
            shrink_callbacks=[lambda: self.filters.hide()],
            expand_callbacks=[lambda: self.filters.show()],
        )

        self.row_edit = EditDialog(
            self.table_display,
            filter_dependencies=filter_dependencies,
            open_dialog_button=self.edit_button,
            submit_callbacks=[lambda: self.lazyfilter.update({})],
        )
        self.fullscreen = Dialog(
            open_dialog_button=self.fullscreen_button,
            content=[self._fullscreen_content],
        )

        self.buttons.children = [self.filter_button, self.row_edit, self.fullscreen]

        self.table_display.table.observe(self._set_row_edit_data, "v_model")

    def _set_row_edit_data(self, change):
        row_data = change["new"]
        if len(row_data) == 0:
            row_data = None
        else:
            row_data = self.table_display.dataframe.loc[int(row_data[0]["index"])]
        self.row_edit.row_data = row_data

    @property
    def _fullscreen_content(self):
        buttons = v.Html(  # type: ignore
            tag="div",
            class_="d-flex flex-column justify-start",
            children=[self.filter_button, self.row_edit],
        )
        return ContentWithSidebar(
            sidebar_content=[buttons, self.filters],
            content=[self.table_display],
            toggle_sidebar_button=self.filter_button,
            toggle_callbacks=[
                lambda: buttons.class_list.toggle("flex-column", "flex-row")
            ],
            shrink_callbacks=[lambda: self.filters.hide()],
            expand_callbacks=[lambda: self.filters.show()],
        )
