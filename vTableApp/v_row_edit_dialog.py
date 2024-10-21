import ipyvuetify as v
import pandas as pd

from .v_bounded_float_field import BoundedFloatField
from .v_dataframe_filter import _DataFrameFilter, lazy_filter
from .v_dialog import Dialog
from .v_autocomplete import Autocomplete


class EditDialog(Dialog):
    def __init__(
        self,
        table_display,
        *,
        open_dialog_button,
        submit_callbacks=None,
    ):
        self.table_display = table_display
        self.row_data = None
        self.strict = v.Switch(v_model=True, label="strict", class_="pa-4")
        self.undo_button = v.Btn(
            icon=True, children=[v.Icon(children=["mdi-undo-variant"])], class_="mx-4"
        )
        self.confirm_button = v.Btn(
            icon=True, children=[v.Icon(children=["mdi-check"])], class_="ma-4"
        )
        self.fields_layout = v.Layout(class_="d-flex wrap pa-2", children=[])
        super().__init__(
            open_dialog_button=open_dialog_button,
            fullscreen=False,
            title="Edit row values",
            content=[
                self.fields_layout,
                v.CardActions(
                    children=[
                        self.strict,
                        v.Spacer(),
                        self.undo_button,
                        self.confirm_button,
                    ],
                ),
            ],
            open_callbacks=[self.get_edit_widgets],
            close_callbacks=[self.close_edit_widgets],
        )
        self.submit_callbacks = submit_callbacks
        self.strict.observe(lambda *args: self.get_edit_widgets(), "v_model")
        self.undo_button.on_event("click", self.undo)
        self.confirm_button.on_event("click", self.submit)

    def get_values(self, *, from_data=False, lazyfilter=None):
        def row_data_value(column):
            if self.row_data is None:
                raise ValueError("no row data available")
            if column == pd.Index:
                return self.row_data.name
            return self.row_data[column]

        if self.row_data is None:
            raise ValueError("no row data available")
        values = {}
        if len(self.fields_layout.children) > 0 and not from_data:
            for column, widget in zip(
                [pd.Index] + list(self.row_data.keys()), self.fields_layout.children
            ):
                values[column] = (
                    widget.value
                    if isinstance(widget, BoundedFloatField)
                    else widget.v_model
                )
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
            return values
        for column in [pd.Index] + list(self.row_data.keys()):
            values[column] = row_data_value(column)
        return values

    def undo(self, *args):
        values = self.get_values(from_data=True)
        for widget, value in zip(self.fields_layout.children, values.values()):
            if isinstance(widget, BoundedFloatField):
                # this is a bit hacky, but sometimes an error rule can prevent setting value directly
                widget.value = widget.min
                widget.value = float(value)
            else:
                widget.v_model = value

    def close_edit_widgets(self):
        self.fields_layout.children = []

    def get_edit_widgets(self):
        if self.row_data is None:
            return False
        style = "width: 200px"
        class_ = "pa-4"
        widgets = []
        lazyfilter = lazy_filter(
            self.table_display,
            track_description=False,
        )
        # make sure that this is actually the monkey patched DataFrameFilter
        assert isinstance(lazyfilter, _DataFrameFilter)
        values = self.get_values(lazyfilter=lazyfilter)
        for column, entry_type, options, _ in list(lazyfilter.description.values()):
            value = values[column]
            filter = lazyfilter.get(column, filter_type=entry_type)
            column_name = lazyfilter.column_name(filter)
            if column == pd.Index:
                widget = BoundedFloatField(
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
                step = lazyfilter.panels[id(filter)].children[1].children[0].step
                if self.strict.v_model:
                    widget = BoundedFloatField(
                        min=float(options[0]),
                        max=float(options[1]),
                        value=float(value),
                        step=step,
                        label=f"Insert {column_name}",
                        class_=class_,
                        style_=style,
                    )
                else:
                    widget = v.TextField(
                        v_model=value,
                        attributes={"step": step},
                        type="number",
                        label=f"Insert {column_name}",
                        class_=class_,
                        style_=style,
                    )
            elif entry_type == "selected_values":
                if self.strict.v_model or isinstance(
                    filter.values.dtype, pd.CategoricalDtype
                ):
                    widget = Autocomplete(
                        v_model=value,
                        chips=False,
                        multiple=False,
                        items=list(options),
                        label=f"Insert {column_name}",
                        class_=class_,
                        style_=style,
                    )
                else:
                    widget = v.TextField(
                        v_model=value,
                        label=f"Insert {column_name}",
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
            column_data = self.table_display.dataframe[column].astype(type(value))
            try:
                column_data.loc[row_idx] = value
                self.table_display.dataframe.loc[:, column] = column_data.astype(
                    self.table_display.dataframe[column].dtype
                )
            except Exception as e:
                print(f"error setting {value} to {column}")
                print(e)
        self.table_display._set_items(index=self.table_display.current_index)
        self.row_data = self.table_display.dataframe.loc[row_idx]
        self._close_dialog()
        if self.submit_callbacks is not None:
            for callback in self.submit_callbacks:
                callback()
