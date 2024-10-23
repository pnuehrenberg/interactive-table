import ipyvuetify as v
import lazyfilter
import pandas as pd
import traitlets

from .traitlet_utils import MutableDict
from .v_checkable_expansion_panel import CheckableExpansionPanel
from .v_range_filter import RangeFilter
from .v_selection_filter import SelectionFilter


class _DataFrameFilter(v.ExpansionPanels, lazyfilter.DataFrameFilter):
    description = MutableDict()  # type: ignore

    def __init__(self, dataframe, callbacks=None, track_description=True, **kwargs):
        v.ExpansionPanels.__init__(self, v_model=[], **kwargs)
        self.dataframe = dataframe
        self.dependencies = {}
        self.track_description = track_description
        self.panels = {}
        self.callbacks = callbacks

    def add(self, filter, *, dependencies=None):
        def callback(selection):
            self.update({filter.column: selection})

        super().add(filter, dependencies=dependencies)
        column_name = self.column_name(filter)
        if filter.selected_values is None:
            filter_widget = RangeFilter(
                values=filter.values,
                allow_quantile_range_filter=filter.column != pd.Index,
                callbacks=[callback],
            )
        else:
            filter_widget = SelectionFilter(
                values=filter.values,
                callbacks=[callback],
                label=f"Select {column_name}",
            )
        widget = CheckableExpansionPanel(
            title=column_name.capitalize(),
            content=[filter_widget],
            reset_callbacks=[filter_widget.reset, filter.reset],
        )
        self.panels[id(filter)] = widget
        self.children = list(self.children) + [widget]
        # describe filter, but temporarily deactivate callbacks for initial description
        callbacks = self.callbacks
        self.callbacks = None
        self.describe(filter)
        self.callbacks = callbacks

    def _set_checked(self, filter):
        widget = self.panels[id(filter)].children[1].children[0]
        if not filter.is_active:
            self.panels[id(filter)].checked = False
            return
        is_filtering = True
        if filter.filter_type == "quantile_range" and filter.value == (0, 1):
            is_filtering = False
        if filter.filter_type == "value_range" and filter.value == (widget.min, widget.max):
            is_filtering = False
        if filter.filter_type == "selected_values" and (value := filter.value) is not None and len(value) == 0:
            is_filtering = False
        self.panels[id(filter)].checked = is_filtering

    @traitlets.observe("description", type="mutation")
    def _description_change(self, change):
        for key in change["new"]:
            column, filter_type, options, value = change["new"][key]
            filter = self.get(column)
            widget = self.panels[id(filter)].children[1].children[0]
            widget.values = options # filter.values  # check values property for both widget types
            if filter.is_active:
                widget.value = value # filter.value
            else:
                widget.reset()
            self._set_checked(filter)
        if self.callbacks is None:
            return
        filtered_dataframe = self.apply(track_description=False)
        for callback in self.callbacks:
            callback(filtered_dataframe)


lazyfilter.lazy.DataFrameFilter = _DataFrameFilter
lazy_filter = lazyfilter.lazy.lazy_filter
