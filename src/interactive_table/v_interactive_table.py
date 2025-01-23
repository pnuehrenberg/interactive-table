import ipyvuetify as v
import ipywidgets as widgets
import numpy as np
import pandas as pd
import traitlets
from lazyfilter.utils import HasValidDataframe

from .v_dataframe_filter import _DataFrameFilter, lazy_filter


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


def parse_dtype(dataframe, column_name):
    dtype = dataframe[column_name].dtype
    is_bool = dtype == "bool"
    is_int = dtype == "int"
    is_float = dtype == "float"
    is_categorical = isinstance(dtype, pd.CategoricalDtype)
    is_string = dtype == "O"
    if sum(map(int, [is_bool, is_int, is_float, is_categorical, is_string])) != 1:
        raise ValueError(f"{column_name} has unsupported dtype {dtype}")
    return dtype, {
        "bool": is_bool,
        "int": is_int,
        "float": is_float,
        "categorical": is_categorical,
        "O": is_string,
    }


class _TableDisplay(HasValidDataframe, v.VuetifyTemplate):  # type: ignore
    selected = traitlets.Any().tag(sync=True)
    headers = traitlets.Any().tag(sync=True)
    items = traitlets.List().tag(sync=True)
    uniques = traitlets.Dict().tag(sync=True)
    input_error = traitlets.Any().tag(sync=True)
    filter_widgets = traitlets.List().tag(sync=True, **widgets.widget_serialization)
    editing = traitlets.Bool().tag(sync=True)
    show_filter_snackbar = traitlets.Bool().tag(sync=True)
    filter_snackbar_timeout = traitlets.Int().tag(sync=True)
    fullscreen_icon = traitlets.Unicode().tag(sync=True)
    action_dialogs = traitlets.List().tag(sync=True, **widgets.widget_serialization)

    @traitlets.default("template")
    def _template(self):
        return f"""
            <v-template>
                <v-data-table
                    :headers="headers"
                    :items="items"
                    item-key="index"
                    multi-sort
                    :footer-props="{{
                        showFirstLastPage: true,
                        itemsPerPageOptions: [5, 10, 15, 25, 50, -1],
                    }}"
                    :items-per-page=10
                    >
                    {
                        '\n'.join(
                            [
                                self._generate_input_slot_template(header_item["value"])
                                for header_item in self.headers
                                if header_item["value"] != "index"
                            ]
                        )
                    }
                    <template slot="header" :headers="headers">
                        <tr>
                            <th v-for="(header, index) in headers"
                                :key="header.value">
                                <jupyter-widget :widget="filter_widgets[index]" />
                            </th>
                        </tr>
                    </template>

                    <template v-slot:footer>
                        <v-btn
                            fab
                            icon
                            small
                            elevation=0
                            absolute
                            center
                            left
                            class="mt-3"
                            @click="toggle_fullscreen"
                        >
                            <v-icon>{{{{ fullscreen_icon }}}}</v-icon>
                        </v-btn>
                    </template>

                </v-data-table>

                <v-snackbar
                    v-model="show_filter_snackbar"
                    :timeout="filter_snackbar_timeout"
                    color="white"
                    >
                    <div class="black--text">Apply filters?</div>
                    <v-spacer></v-spacer>
                    <v-btn text color="primary" @click="show_filter_snackbar = false">No</v-btn>
                    <v-btn text color="primary" @click="apply_filters">Yes</v-btn>
                </v-snackbar>

                <jupyter-widget v-for="dialog in action_dialogs" :widget="dialog" />

            </v-template>
            """

    def vue_action_click(self, args):
        item, action_name = args
        self.actions[action_name](item)

    def _generate_input_slot_template(self, column_name):
        if column_name == "actions":
            return f"""
            <template v-slot:item.{column_name}="props">
                <div class="d-inline-flex flex-row flex-nowrap align-self-start">
                    {
                        '\n'.join(
                            [
                                f"""
                                <v-btn
                                    icon
                                    @click.native.stop="action_click([props.item, '{action_name}'])"
                                    >
                                    <v-icon>{action_name}</v-icon>
                                </v-btn>
                                """
                                for action_name in self.actions
                            ]
                        )
                    }
                </div>
            </template>
            """
        dtype, topts = parse_dtype(self.dataframe, column_name)
        text_field = f"""
            <v-text-field
                v-model="props.item.{column_name}"
                :rules="[validate_{column_name}]"
                :error-messages="input_error"
                type="{"number" if topts["float"] or topts["int"] else "text"}"
                step={1 if topts["int"] else 0.1}
                >
            </v-text-field>
            """
        selection = f"""
            <v-autocomplete
                :items="uniques.{column_name}"
                v-model="props.item.{column_name}"
            >
            </v-autocomplete>
            """
        checkbox = f"""
            <v-simple-checkbox
                v-model="props.item.{column_name}"
                >
            </v-simple-checkbox>
            """
        dialog = f"""
            <v-edit-dialog
                save-text="OK"
                large
                lazy
                :return-value.sync="props.item.{column_name}"
                @open="editing = true"
                @save="on_edit_submit"
                @close="on_edit_close"
                >
                    <v-hover v-slot="{{ hover }}">
                        <div :class="hover ? 'primary--text' : ''">
                            {f"{{{{ props.item.{column_name} }}}}" if not topts["float"] else f"{{{{ props.item.{column_name}.toFixed(3) }}}}"}
                        </div>
                    </v-hover>
                    <template v-slot:input>
                        {selection if topts["categorical"] else text_field}
                    </template>
            </v-edit-dialog>
            """
        return f"""
            <template v-slot:item.{column_name}="props">
                {checkbox if topts["bool"] else dialog}
            </template>
            """

    def __init__(
        self,
        data_table,
        dataframe,
        *,
        filter_dependencies,
        show_index,
        show_actions,
        actions,
        action_dialogs,
    ):
        self._data_table = data_table
        self.fullscreen_icon = "mdi-fullscreen"
        self.actions = {} if actions is None else actions
        self.action_dialogs = [] if action_dialogs is None else action_dialogs
        self.dataframe = dataframe
        self.selected = []
        self._set_headers(show_index=show_index, show_actions=show_actions)
        self._set_items()
        self.lazyfilter = lazy_filter(
            self,
            dependencies=filter_dependencies,
            track_description=True,
            callbacks=[lambda dataframe: self._set_items(index=dataframe.index)],
        )
        assert isinstance(self.lazyfilter, _DataFrameFilter)
        # make sure that this is the monkey-patched data frame filter class
        self.filter_widgets = [
            self.lazyfilter.widgets[filter] for filter in self.lazyfilter.dependencies
        ]
        for header_item in self.headers:
            column_name = header_item["value"]
            if column_name in ["index", "actions"]:
                continue

            def validation_func(value, column_name=column_name):
                return self._validate(column_name, value)

            setattr(self, f"vue_validate_{column_name}", validation_func)
            dtype, topts = parse_dtype(self.dataframe, column_name)
            if topts["categorical"]:
                self.uniques[column_name] = list(dtype.categories)  # type: ignore
            elif topts["O"]:
                self.uniques[column_name] = np.unique(
                    self.dataframe[column_name]
                ).tolist()
        v.VuetifyTemplate.__init__(self)  # type: ignore

    def _validate(self, column_name, value):
        dtype, topts = parse_dtype(self.dataframe, column_name)
        if topts["int"]:
            try:
                cast(str(value), dtype)
                self.input_error = None
            except ValueError:
                self.input_error = "Input must be whole number."
                return False
        if topts["float"]:
            try:
                cast(str(value), dtype)
                self.input_error = None
            except ValueError:
                self.input_error = "Input must be numeric."
        return True

    def _set_headers(self, *, show_index, show_actions):
        headers = [
            {"text": column.replace("_", " ").capitalize(), "value": column}
            for column in self.dataframe
        ]
        if show_index:
            headers = [{"text": "Index", "value": "index"}] + headers
        if show_actions and len(self.actions) > 0:
            headers.append({"text": "Actions", "value": "actions", "sortable": False})  # type: ignore
        self.headers = headers

    @property
    def current_index(self):
        return pd.Index([item["index"] for item in self.items])

    def _get_items(self, *, index=None):
        if index is None:
            index = self.dataframe.index
        return [
            {"index": idx, **item, "actions": None}
            for idx, item in zip(
                index, self.dataframe.loc[index].to_dict(orient="records")
            )
        ]

    def _set_items(self, *, index=None):
        self.items = self._get_items(index=index)

    @traitlets.observe("items")
    def _on_item_change(self, change):
        if change["old"] == traitlets.Undefined:
            return
        submit_changes = {}
        for new_item in change["new"]:
            row = {}
            index = new_item["index"]
            for column_name, value in new_item.items():
                if column_name in ["index", "actions"]:
                    continue
                try:
                    row[column_name], dtype = cast(
                        str(value), self.dataframe[column_name].dtype
                    )
                    if dtype != self.dataframe[column_name].dtype:
                        return
                except ValueError:
                    return
            row = pd.Series(row, name=index)
            if not (row == self.dataframe.loc[index]).all():
                submit_changes[index] = row
        changed = False
        for index, row in submit_changes.items():
            self.dataframe.loc[index] = row
            changed = True
        if not changed:
            return
        selection = {
            column_name: (filter_type, value)
            for (
                column_name,
                filter_type,
                *_,
                value,
            ) in self.lazyfilter.description.values()
            if self.lazyfilter.get(column_name).is_active
        }
        assert isinstance(self.lazyfilter, _DataFrameFilter)
        with self.lazyfilter.block_callbacks():
            self.lazyfilter.update(selection, reset=True)
        if not self.editing:
            self.show_filter_snackbar = True
            self.filter_snackbar_timeout = 5000

    def vue_on_edit_close(self, args):
        self.editing = False

    def vue_on_edit_submit(self, args):
        self.editing = False
        self._set_items(index=self.current_index)
        self.show_filter_snackbar = True
        self.filter_snackbar_timeout = 5000

    def vue_apply_filters(self, args):
        self.show_filter_snackbar = False
        self._set_items(index=self.lazyfilter.apply().index)

    def vue_toggle_fullscreen(self, args):
        self._data_table.toggle_fullscreen()


class InteractiveTable(v.Col):
    def __init__(
        self,
        dataframe,
        *,
        filter_dependencies=None,
        show_index=True,
        show_actions=True,
        actions=None,
        action_dialogs=None,
    ):
        self.fullscreen = False
        self.display = _TableDisplay(
            self,
            dataframe,
            filter_dependencies=filter_dependencies,
            show_index=show_index,
            show_actions=show_actions,
            actions=actions,
            action_dialogs=action_dialogs,
        )
        self.content = v.Card(
            children=[v.Sheet(class_="pa-4", children=[self.display])]
        )
        self.fullscreen_display = v.Dialog(
            v_model=False,
            fullscreen=True,
            children=[],
        )
        super().__init__(children=[self.display, self.fullscreen_display])

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.fullscreen_display.children = [self.content]
            self.display.fullscreen_icon = "mdi-fullscreen-exit"
            self.fullscreen_display.v_model = True
            self.children = [self.fullscreen_display]
        else:
            self.children = [self.display, self.fullscreen_display]
            self.fullscreen_display.children = []
            self.display.fullscreen_icon = "mdi-fullscreen"
            self.fullscreen_display.v_model = False
