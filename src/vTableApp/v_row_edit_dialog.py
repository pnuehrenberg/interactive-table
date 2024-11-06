import ipyvuetify as v
import numpy as np
import pandas as pd

from .v_autocomplete import Autocomplete
from .v_bounded_input import BoundedInput
from .v_dataframe_filter import _DataFrameFilter, lazy_filter
from .v_dialog import Dialog


def cast(value, dtype):
    try:
        if dtype == "bool":
            value = str(value).lower() == "true"
        elif dtype == "int":
            value = int(value)
        elif dtype == "float":
            value = float(value)
        elif dtype == "O":
            value = str(value)
        elif isinstance(dtype, pd.CategoricalDtype):
            categories = dtype.categories
            value, _ = cast(value, categories.dtype)
            if value not in categories:
                dtype = pd.CategoricalDtype(list(categories) + [value])
    except ValueError:
        raise ValueError("Unsupported type")
    return value, dtype


def _get_widget_value(widget):
    if isinstance(widget, BoundedInput):
        return widget.value
    if isinstance(widget, Autocomplete):
        return widget.selection
    return widget.v_model


def _set_widget_value(widget, value):
    if isinstance(widget, BoundedInput):
        widget.value = float(value)
        return
    if isinstance(widget, Autocomplete):
        widget.selection = value
        return
    widget.v_model = value


class EditDialog(Dialog):
    def __init__(
        self,
        table_display,
        *,
        submit_callbacks=None,
    ):
        if submit_callbacks is None:
            submit_callbacks = []
        self.table_display = table_display
        self._row_data = None
        self.strict = v.Switch(
            v_model=True, label="strict", hide_details=True, class_="pa-0 pl-2 ma-0"
        )
        self.undo_button = v.Btn(
            icon=True, children=[v.Icon(children=["mdi-undo-variant"])]
        )
        self.placeholder = v.Layout(
            children=["No row selected"],
            class_="d-flex align-center justify-center",
            style_="min-width: 400px; min-height: 100px",
        )
        self.fields_layout = v.Layout(
            class_="d-flex wrap ma-2", children=[self.placeholder]
        )
        super().__init__(
            open_button="mdi-pencil",
            open_button_icon=True,
            fullscreen=False,
            title="Edit row values",
            content=[self.fields_layout],
            actions=[self.strict, v.Spacer(), self.undo_button],
            on_submit_callbacks=[self.submit] + submit_callbacks,
        )
        self.strict.observe(lambda *args: self.get_edit_widgets(), "v_model")
        self.undo_button.on_event("click", self.undo)

    @property
    def row_data(self):
        return self._row_data

    @row_data.setter
    def row_data(self, row_data):
        if row_data is None and self.row_data is None:
            return
        self._row_data = row_data
        if row_data is not None:
            self.get_edit_widgets(copy_widget_data=False)
        else:
            self.close_edit_widgets()

    def get_values(self, *, from_data=False, lazyfilter=None):
        def to_scalar(value):
            if isinstance(value, np.generic):
                return value.item()
            return value

        def row_data_value(column):
            if self.row_data is None:
                raise ValueError("no row data available")
            if column == pd.Index:
                return self.row_data.name
            return self.row_data[column]

        if self.row_data is None:
            raise ValueError("no row data available")
        values = {}
        if len(self.fields_layout.children) > 1 and not from_data:
            for column, widget in zip(
                [pd.Index] + list(self.row_data.keys()), self.fields_layout.children
            ):
                values[column] = _get_widget_value(widget)
            if lazyfilter is not None:
                for column, entry_type, options, _ in list(
                    lazyfilter.description.values()
                ):
                    value = values[column]
                    if entry_type == "selected_values" and value not in options:
                        value = row_data_value(column)
                    elif entry_type == "value_range" and not (
                        float(value) >= options[0] and float(value) <= options[1]
                    ):
                        value = row_data_value(column)
                    values[column] = value
        else:
            for column in [pd.Index] + list(self.row_data.keys()):
                values[column] = row_data_value(column)
        for column, value in values.items():
            values[column] = to_scalar(value)
        return values

    def undo(self, *args):
        if self.row_data is None:
            return
        values = self.get_values(from_data=True)
        for widget, value in zip(self.fields_layout.children, values.values()):
            _set_widget_value(widget, value)

    def close_edit_widgets(self):
        self.fields_layout.children = [self.placeholder]
        return True

    def get_edit_widgets(self, *, copy_widget_data=True):
        if self.row_data is None:
            return False
        style = "min-width: 180px; max-width: 180px"
        class_ = "ma-2"
        widgets = []
        lazyfilter = lazy_filter(
            self.table_display,
            track_description=False,
        )
        # make sure that this is actually the monkey patched DataFrameFilter
        assert isinstance(lazyfilter, _DataFrameFilter)
        values = self.get_values(from_data=not copy_widget_data, lazyfilter=lazyfilter)
        for column, entry_type, options, _ in list(lazyfilter.description.values()):
            value = values[column]
            filter = lazyfilter.get(column, filter_type=entry_type)
            column_name = lazyfilter.column_name(filter)
            if column == pd.Index:
                widget = BoundedInput(
                    min=float(options[0]),
                    max=float(options[1]),
                    value=float(value),
                    step=1,
                    label="Index",
                    readonly=True,
                    class_=class_,
                    style_=style,
                )
            elif entry_type == "value_range":
                step = lazyfilter.widgets[filter].content.content[0].step
                if self.strict.v_model:
                    widget = BoundedInput(
                        min=float(options[0]),
                        max=float(options[1]),
                        value=float(value),
                        step=step,
                        label=column_name.capitalize(),
                        class_=class_,
                        style_=style,
                    )
                else:
                    widget = v.TextField(
                        v_model=value,
                        attributes={"step": step},
                        type="number",
                        label=column_name.capitalize(),
                        class_=class_,
                        style_=style,
                    )
            elif entry_type == "selected_values":
                if self.strict.v_model:
                    widget = Autocomplete(
                        selection=value,
                        chips=False,
                        multiple=False,
                        items=list(options),
                        label=column_name.capitalize(),
                        class_=class_,
                        style_=style,
                    )
                else:
                    widget = v.TextField(
                        v_model=value,
                        label=column_name.capitalize(),
                        class_=class_,
                        style_=style,
                    )
            else:
                raise ValueError
            widgets.append(widget)
        self.fields_layout.children = widgets
        return True

    def submit(self, *args):
        values = self.get_values()
        row_idx = values[pd.Index]
        for column, value in values.items():
            if column == pd.Index:
                continue
            dtype = self.table_display.dataframe[column].dtype
            value, dtype_cast = cast(value, dtype)
            if dtype == dtype_cast:
                self.table_display.dataframe.loc[row_idx, column] = value
            else:
                self.table_display.dataframe[column] = self.table_display.dataframe[
                    column
                ].astype(dtype_cast)
                self.table_display.dataframe.loc[row_idx, column] = value
        self.table_display._set_items(index=self.table_display.current_index)
        self.row_data = self.table_display.dataframe.loc[row_idx]
        return True
